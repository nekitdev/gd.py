import asyncio
import signal
import traceback

from gd.async_utils import acquire_loop, shutdown_loop, gather
from gd.enums import TimelyType
from gd.filters import Filters
from gd.level import Level
from gd.logging import get_logger
from gd.text_utils import make_repr
from gd.typing import (
    Any,
    AsyncIterator,
    List,
    Optional,
    Sequence,
    TypeVar,
    TYPE_CHECKING,
)

__all__ = (
    "AbstractListener",
    "TimelyLevelListener",
    "RateLevelListener",
    "MessageOrRequestListener",
    "LevelCommentListener",
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


def set_loop(new_loop: asyncio.AbstractEventLoop) -> None:
    """Set loop for running listeners to new_loop."""
    global loop

    loop = new_loop


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
        shutdown_loop(loop)


class AbstractListener:
    """Abstract listener for listeners to derive from."""

    def __init__(self, client: "Client", delay: float = 10.0) -> None:
        self.client = client
        self.delay = delay

        self.cache: Any = None

        self.loop: asyncio.AbstractEventLoop = acquire_loop(running=True)

        all_listeners.append(self)

    def __repr__(self) -> str:
        info = {"client": self.client}
        return make_repr(self, info)

    async def on_error(self, error: Exception) -> None:
        """Basic event handler to print the errors if any occur."""
        traceback.print_exc()

    async def setup(self) -> None:
        """This function is used to do some preparations before starting listeners."""
        pass

    async def scan(self) -> None:
        """This function should contain main code of the listener."""
        pass

    async def main(self) -> None:
        """Main function, that is basically doing all the job."""
        await self.setup()

        try:
            self.loop = acquire_loop(running=True)
            await self.scan()

        except Exception as exc:
            await self.on_error(exc)


class TimelyLevelListener(AbstractListener):
    """Listens for a new daily or weekly level."""

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
    """Listens for a new rated or unrated level."""

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
        new = await self.client.search_levels(filters=self.filters, pages=range(self.pages))

        if not new:  # servers are probably broken, abort
            return

        if not self.cache:
            self.cache = new
            return

        difference = differ(self.cache, new, self.find_new)

        self.cache = new

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
    """Listens for a new friend request or message."""

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
        new = await self.get_entities()  # type: ignore

        if not new:
            return

        if not self.cache:
            self.cache = new
            return

        difference = differ(self.cache, new, find_new=True)

        if self.read:
            await gather(entity.read() for entity in difference)

        self.cache = new

        for entity in difference:
            dispatcher = self.client.dispatch(self.to_call, entity)
            self.loop.create_task(dispatcher)


MessageListener = MessageOrRequestListener
RequestListener = MessageOrRequestListener


class LevelCommentListener(AbstractListener):
    """Listens for a new comment on a level."""

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
        """Scan for new comments on a level."""
        new = await self.level.get_comments(amount=self.amount)

        if not new:
            return

        if not self.cache:
            self.cache = new
            return

        difference = differ(self.cache, new, find_new=True)

        self.cache = new

        if difference and self.refresh:
            await self.level.refresh()

        for comment in difference:
            dispatcher = self.client.dispatch(self.to_call, self.level, comment)
            self.loop.create_task(dispatcher)


def differ(before: Sequence[T], after: Sequence[T], find_new: bool = True) -> Sequence[T]:
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
