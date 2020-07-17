import asyncio
import signal
import traceback

from gd.level import Level
from gd.logging import get_logger
from gd.typing import (
    Client,
    Comment,
    FriendRequest,
    Iterable,
    Iterator,
    List,
    Message,
    TypeVar,
    Union,
)

from gd.utils.async_utils import acquire_loop, shutdown_loop, gather
from gd.utils.enums import TimelyType
from gd.utils.filters import Filters
from gd.utils.text_tools import make_repr

__all__ = (
    "AbstractListener",
    "TimelyLevelListener",
    "RateLevelListener",
    "MessageOrRequestListener",
    "LevelCommentListener",
    "get_loop",
    "set_loop",
    "run",
    "differ",
    "all_listeners",
)

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


def run(loop: asyncio.AbstractEventLoop) -> None:
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

    def __init__(self, client: Client, delay: float = 10.0) -> None:
        self.client = client
        self.delay = delay
        self.cache = None
        self.loop: asyncio.AbstractEventLoop = acquire_loop(running=True)

        all_listeners.append(self)

    def __repr__(self) -> str:
        info = {"client": self.client}
        return make_repr(self, info)

    async def on_error(self, exc: Exception) -> None:
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

    def __init__(self, client: Client, timely_type: str, delay: int = 10.0) -> None:
        super().__init__(client=client, delay=delay)
        self.method = getattr(client, "get_" + timely_type)
        self.call_method = "new_" + timely_type

    async def scan(self) -> None:
        """Scan for either daily or weekly levels."""
        timely = await self.method()

        if self.cache is None:
            self.cache = timely
            return

        if timely.id != self.cache.id:
            dispatcher = self.client.dispatch(self.call_method, timely)
            self.loop.create_task(dispatcher)  # schedule the execution

        self.cache = timely


class RateLevelListener(AbstractListener):
    """Listens for a new rated or unrated level."""

    def __init__(self, client: Client, listen_to_rate: bool = True, delay: float = 10.0) -> None:
        super().__init__(client=client, delay=delay)
        self.call_method = "level_rated" if listen_to_rate else "level_unrated"
        self.filters = Filters(strategy="awarded")
        self.find_new = listen_to_rate

    async def method(self, pages: int = 5) -> List[Level]:
        return await self.client.search_levels(filters=self.filters, pages=range(pages))

    async def scan(self) -> None:
        """Scan for rated/unrated levels."""
        new = await self.method()

        if not new:  # servers are probably broken, abort
            return

        if not self.cache:
            self.cache = new
            return

        difference = differ(self.cache, new, self.find_new)

        self.cache = new

        for level in await rating_differ(difference, self.find_new):
            dispatcher = self.client.dispatch(self.call_method, level)
            self.loop.create_task(dispatcher)


async def rating_differ(array: Iterable[Level], find_new: bool = True) -> List[Level]:
    array = list(array)
    updated = await gather(level.refresh() for level in array)
    final = []

    for level, new in zip(array, updated):
        if find_new:
            if new.is_rated() or new.has_coins_verified():
                final.append(new)
        else:
            if new is None:
                final.append(level)
            elif not new.is_rated() and not new.has_coins_verified():
                final.append(new)

    return final


class MessageOrRequestListener(AbstractListener):
    """Listens for a new friend request or message."""

    def __init__(self, client: Client, listen_messages: bool = True, delay: float = 5.0) -> None:
        super().__init__(client=client, delay=delay)
        self.to_call = "message" if listen_messages else "friend_request"
        self.method = getattr(
            client, ("get_messages" if listen_messages else "get_friend_requests")
        )

    async def call_method(self, pages: int = 10) -> Union[List[FriendRequest], List[Message]]:
        return await self.method(pages=range(pages))

    async def scan(self) -> None:
        """Scan for new friend requests or messages."""
        new = await self.call_method()

        if not new:
            return

        if not self.cache:
            self.cache = new
            return

        difference = list(differ(self.cache, new, True))

        await gather(entity.read() for entity in difference)

        self.cache = new

        for entity in difference:
            dispatcher = self.client.dispatch(self.to_call, entity)
            self.loop.create_task(dispatcher)


class LevelCommentListener(AbstractListener):
    """Listens for a new comment on a level."""

    def __init__(self, client: Client, level_id: int, delay: float = 10.0) -> None:
        super().__init__(client=client, delay=delay)
        self.call_method = "level_comment"
        self.timely_type = TimelyType(-level_id if level_id < 0 else 0)
        self.level = Level(id=level_id, type=self.timely_type, client=self.client)

    async def method(self, amount: int = 1000) -> List[Comment]:
        return await self.level.get_comments(amount=amount)

    async def scan(self) -> None:
        """Scan for new comments on a level."""
        new = await self.method()

        if not new:
            return

        if not self.cache:
            self.cache = new
            return

        difference = differ(self.cache, new, True)

        self.cache = new

        if difference:
            await self.level.refresh()

        for comment in difference:
            dispatcher = self.client.dispatch(self.call_method, self.level, comment)
            self.loop.create_task(dispatcher)


def differ(before: List[T], after: List[T], find_new: bool = True) -> Iterator[T]:
    # this could be improved a lot ~ nekit
    if find_new:
        for item in before:
            # find a pivot
            try:
                after = after[: after.index(item)]
                break
            except ValueError:  # not in list
                pass

    list_not_in, list_in = (before, after) if find_new else (after, before)
    return filter(lambda elem: (elem not in list_not_in), list_in)
