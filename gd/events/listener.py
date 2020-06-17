import asyncio
import threading
import signal
import traceback

from gd.level import Level
from gd.logging import get_logger
from gd.typing import Client, Comment, FriendRequest, Iterable, List, Message, Optional, Union

from gd.utils import tasks
from gd.utils.async_utils import shutdown_loop, gather
from gd.utils.decorators import run_once
from gd.utils.enums import TimelyType
from gd.utils.filters import Filters
from gd.utils.text_tools import make_repr

__all__ = (
    "AbstractListener",
    "TimelyLevelListener",
    "RateLevelListener",
    "MessageOrRequestListener",
    "LevelCommentListener",
    "thread",
    "get_loop",
    "set_loop",
    "run",
    "differ",
    "all_listeners",
)

loop = asyncio.new_event_loop()

log = get_logger(__name__)

all_listeners = []


def get_loop() -> asyncio.AbstractEventLoop:
    return loop


def set_loop(new_loop: asyncio.AbstractEventLoop) -> None:
    global loop
    loop = new_loop


def run(loop: asyncio.AbstractEventLoop) -> None:
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


def update_thread_loop(thread: threading.Thread, loop: asyncio.AbstractEventLoop) -> None:
    thread.args = (loop,)


thread = threading.Thread(target=run, args=(loop,), name="ListenerThread", daemon=True)


class AbstractListener:
    def __init__(
        self,
        client: Client,
        delay: float = 10.0,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        if loop is None:
            loop = get_loop()
        self.client = client
        self.loop = loop
        self.runner = tasks.loop(seconds=delay, loop=loop)(self.main)
        self.cache = None
        all_listeners.append(self)

    def __repr__(self) -> str:
        info = {"client": self.client}
        return make_repr(self, info)

    def attach_to_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Attach the runner to another event loop."""
        self.runner.loop = loop
        self.loop = loop

    def enable(self) -> None:
        try:
            self.runner.start()
        except RuntimeError:
            pass

    @run_once
    def close(self, *args, force: bool = True) -> None:
        """Accurately shutdown a listener.
        If force is true, cancel the runner, and wait until it finishes otherwise.
        """
        if force:
            self.runner.cancel()
        else:
            self.runner.stop()

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
            await self.scan()

        except Exception as exc:
            await self.on_error(exc)


class TimelyLevelListener(AbstractListener):
    """Listens for a new daily or weekly level."""

    def __init__(
        self,
        client: Client,
        t_type: str,
        delay: int = 10.0,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(client, delay, loop=loop)
        self.method = getattr(client, "get_" + t_type)
        self.call_method = "new_" + t_type

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

    def __init__(
        self,
        client: Client,
        listen_to_rate: bool = True,
        delay: float = 10.0,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(client, delay, loop=loop)
        self.client = client
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

        for level in await further_differ(difference, self.find_new):
            dispatcher = self.client.dispatch(self.call_method, level)
            self.loop.create_task(dispatcher)


async def further_differ(array: Iterable[Level], find_new: bool = True) -> List[Level]:
    array = list(array)
    updated = await gather(level.refresh() for level in array)
    final = list()

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

    def __init__(
        self,
        client: Client,
        listen_to_msg: bool = True,
        delay: float = 5.0,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(client, delay, loop=loop)
        self.client = client
        self.to_call = "message" if listen_to_msg else "friend_request"
        self.method = getattr(client, ("get_messages" if listen_to_msg else "get_friend_requests"))

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

    def __init__(
        self,
        client: Client,
        level_id: int,
        delay: float = 10.0,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(client, delay, loop=loop)
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


def differ(before: list, after: list, find_new: bool = True) -> filter:
    # this could be improved a lot ~ nekit
    if find_new:
        for item in before:
            # find a pivot
            try:
                after = after[: after.index(item)]
                break
            except ValueError:  # not in list
                pass

    a, b = (before, after) if find_new else (after, before)
    return filter(lambda elem: (elem not in a), b)
