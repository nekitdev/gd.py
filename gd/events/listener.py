import asyncio
import signal
import traceback
from functools import partial

from gd.async_iters import AwaitableIterator
from gd.async_utils import gather, get_maybe_running_loop, get_running_loop, shutdown_loop
from gd.comment import Comment
from gd.enums import TimelyType
from gd.filters import Filters
from gd.level import Level
from gd.logging import get_logger
from gd.text_utils import make_repr
from gd.typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Iterable,
    List,
    Optional,
    Sequence,
    TypeVar,
)
from gd.user import User

__all__ = (
    "AbstractListener",
    "TimelyLevelListener",
    "RateLevelListener",
    "MessageOrRequestListener",
    "LevelCommentListener",
    "UserCommentListener",
    "get_loop",
    "set_loop",
    "run_loop",
    "differ",
    "all_listeners",
)

if TYPE_CHECKING:
    from gd.client import Client  # noqa

T = TypeVar("T")

loop = asyncio.new_event_loop()

log = get_logger(__name__)

all_listeners = []


def get_loop() -> asyncio.AbstractEventLoop:
    """Get loop for running listeners, optionally refreshing it if closed or running."""
    global loop

    if loop.is_closed() or loop.is_running():
        loop = asyncio.new_event_loop()

    return loop


def set_loop(other_loop: asyncio.AbstractEventLoop) -> None:
    """Set loop for running listeners to other_loop."""
    global loop

    loop = other_loop


def run_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Run a loop and shutdown it after stopping."""
    try:
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        loop.add_signal_handler(signal.SIGTERM, loop.stop)

    except (NotImplementedError, RuntimeError):
        pass

    asyncio.set_event_loop(loop)

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        log.info("Received the signal to terminate the event loop.")

    finally:
        log.info("Cleaning up tasks.")

        try:
            shutdown_loop(loop)

        except Exception:  # noqa
            pass  # uwu


class AbstractListener:
    """Abstract listener for listeners to derive from."""

    def __init__(self, client: "Client", delay: float = 10.0) -> None:
        self.client = client
        self.delay = delay

        self.cache: Any = None

        self.loop: asyncio.AbstractEventLoop = get_maybe_running_loop()

        all_listeners.append(self)

    def __repr__(self) -> str:
        info = {"client": self.client}
        return make_repr(self, info)

    async def on_error(self, error: Exception) -> None:
        """Basic event handler to print the errors if any occur."""
        traceback.print_exc()

    async def setup(self) -> None:
        """This function is used to do some preparations before running scan iteration."""
        pass

    async def scan(self) -> None:
        """This function should contain main code of the listener."""
        pass

    async def main(self) -> None:
        """Main function, that is basically doing all the job."""
        await self.setup()

        try:
            self.loop = get_running_loop()
            await self.scan()

        except Exception as error:
            await self.on_error(error)


class TimelyLevelListener(AbstractListener):
    """Listens for new daily or weekly levels."""

    def __init__(self, client: "Client", daily: bool, delay: float = 10.0) -> None:
        super().__init__(client=client, delay=delay)

        self.get_timely = client.get_daily if daily else client.get_weekly

        self.to_call = "daily" if daily else "weekly"

    async def scan(self) -> None:
        """Scan for either daily or weekly levels."""
        timely = await self.get_timely()

        if self.cache is None:
            self.cache = timely
            return

        if timely.id != self.cache.id:
            dispatcher = self.client.dispatch(self.to_call, timely)
            self.loop.create_task(dispatcher)  # schedule the execution

        self.cache = timely


class RateLevelListener(AbstractListener):
    """Listens for new rated or unrated levels."""

    def __init__(
        self,
        client: "Client",
        rate: bool,
        delay: float = 10.0,
        pages: int = 5,
        ensure: bool = True,
    ) -> None:
        super().__init__(client=client, delay=delay)

        self.filters = Filters(strategy="awarded")
        self.pages = pages

        self.to_call = "rate" if rate else "unrate"

        self.ensure = ensure
        self.find_new = rate

    async def scan(self) -> None:
        """Scan for rated/unrated levels."""
        fetched = await self.client.search_levels(
            filters=self.filters, pages=range(self.pages)
        ).list()

        if not fetched:  # servers are probably broken, abort
            return

        if not self.cache:
            self.cache = fetched
            return

        difference = differ(self.cache, fetched, self.find_new)

        self.cache = fetched

        if self.ensure:
            async for level in rating_differ(difference, self.find_new):
                dispatcher = self.client.dispatch(self.to_call, level)
                self.loop.create_task(dispatcher)

        else:
            for level in difference:
                dispatcher = self.client.dispatch(self.to_call, level)
                self.loop.create_task(dispatcher)


async def rating_differ(not_refreshed: List[Level], find_new: bool = True) -> AsyncIterator[Level]:
    refreshed: List[Optional[Level]] = await gather(
        level.refresh(get_data=False) for level in not_refreshed
    )

    for level, refreshed_level in zip(not_refreshed, refreshed):
        if find_new:
            if refreshed_level is not None and (
                refreshed_level.is_rated() or refreshed_level.has_coins_verified()
            ):
                yield refreshed_level

        else:
            if refreshed_level is None:
                yield level

            elif not refreshed_level.is_rated() and not refreshed_level.has_coins_verified():
                yield refreshed_level


class MessageOrRequestListener(AbstractListener):
    """Listens for new friend requests or messages."""

    def __init__(
        self,
        client: "Client",
        message: bool,
        delay: float = 10.0,
        pages: int = 5,
        read: bool = True,
    ) -> None:
        super().__init__(client=client, delay=delay)

        self.pages = pages
        self.read = read

        self.to_call = "message" if message else "friend_request"
        self.get_entities = client.get_messages if message else client.get_friend_requests

    async def scan(self) -> None:
        """Scan for new friend requests or messages."""
        fetched = await self.get_entities(pages=range(self.pages))  # type: ignore

        if not fetched:
            return

        if not self.cache:
            self.cache = fetched
            return

        difference = differ(self.cache, fetched, find_new=True)

        if self.read:
            await gather(entity.read() for entity in difference)

        self.cache = fetched

        for entity in difference:
            dispatcher = self.client.dispatch(self.to_call, entity)
            self.loop.create_task(dispatcher)


class LevelCommentListener(AbstractListener):
    """Listens for new comments on given level."""

    def __init__(
        self,
        level_id: int,
        client: "Client",
        delay: float = 10.0,
        amount: int = 1000,
        refresh: bool = True,
    ) -> None:
        super().__init__(client=client, delay=delay)

        self.amount = amount
        self.refresh = refresh

        self.to_call = "level_comment"

        self.timely_type = TimelyType(-level_id if level_id < 0 else 0)
        self.level = Level(id=level_id, type=self.timely_type, client=self.client)

    async def scan(self) -> None:
        """Scan for new comments on given level."""
        fetched = await self.level.get_comments(amount=self.amount)

        if not fetched:
            return

        if not self.cache:
            self.cache = fetched
            return

        difference = differ(self.cache, fetched, find_new=True)

        self.cache = fetched

        if difference and self.refresh:
            await self.level.refresh()

        for comment in difference:
            dispatcher = self.client.dispatch(self.to_call, self.level, comment)
            self.loop.create_task(dispatcher)


class UserCommentListener(AbstractListener):
    """Listens for new comments by given user."""

    def __init__(
        self,
        account_id: Optional[int] = None,
        id: Optional[int] = None,
        name: Optional[int] = None,
        profile: bool = True,
        *,
        client: "Client",
        delay: float = 10.0,
        pages: int = 5,
    ) -> None:
        super().__init__(client=client, delay=delay)

        self.pages = pages
        self.to_call = "user_comment"

        if account_id is None:
            if id is None:
                if name is None:
                    raise ValueError("No user selectors were provided")

                else:
                    self.find_user = partial(self.client.search_user, name)

            else:
                self.find_user = partial(self.client.search_user, id)

        else:
            self.find_user = partial(self.client.get_user, account_id)

        self.get_user_comments: Callable[
            [User, Iterable[int], bool], AwaitableIterator[Comment]
        ] = (
            User.get_profile_comments if profile else User.get_comment_history
        )
        self.user: Optional[User] = None

        self.profile = profile

    async def setup(self) -> None:
        """Find user to fetch the comments of."""
        self.user = await self.find_user()

    async def scan(self) -> None:
        """Scan for new comments by user."""
        if self.user is None:
            return

        fetched = await self.get_user_comments(  # type: ignore
            self.user, pages=range(self.pages)  # type: ignore
        ).list()

        if not fetched:
            return

        if not self.cache:
            self.cache = fetched
            return

        difference = differ(self.cache, fetched, find_new=True)

        self.cache = fetched

        for comment in difference:
            dispatcher = self.client.dispatch(self.to_call, self.user, comment)
            self.loop.create_task(dispatcher)


def differ(before: Sequence[T], after: Sequence[T], find_new: bool = True) -> List[T]:
    sequence_not_in, sequence_in = (before, after) if find_new else (after, before)

    set_not_in = set(sequence_not_in)

    if find_new:
        index = 0

        for index, item in enumerate(sequence_in):
            if item in set_not_in:
                break

        else:
            index = len(sequence_in)

        sequence_in = sequence_in[:index]

    return [item for item in sequence_in if item not in set_not_in]
