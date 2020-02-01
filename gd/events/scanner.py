import asyncio
import threading
import signal
import logging
import traceback

from .._typing import AsyncIterator, Iterable, Level, List
from ..client import Client

from ..utils import tasks
from ..utils._async import shutdown_loop
from ..utils.decorators import run_once
from ..utils.filters import Filters

__all__ = (
    'AbstractScanner', 'TimelyLevelScanner', 'RateLevelScanner',
    'thread', 'get_loop', 'set_loop', 'run', 'differ',
    'daily_listener', 'weekly_listener', 'rate_listener', 'unrate_listener',
    'all_listeners'
)

loop = asyncio.new_event_loop()

scanner_client = Client(loop=loop)

log = logging.getLogger(__name__)

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
        log.info('Received the signal to terminate the event loop.')

    finally:
        log.info('Cleaning up tasks.')
        shutdown_loop(loop)


def update_thread_loop(thread: threading.Thread, loop: asyncio.AbstractEventLoop) -> None:
    thread.args = (loop,)


thread = threading.Thread(target=run, args=(loop,), name='ScannerThread', daemon=True)


class AbstractScanner:
    def __init__(self, delay: float = 10.0, *, loop: asyncio.AbstractEventLoop = None) -> None:
        if loop is None:
            loop = get_loop()
        self.loop = loop
        self.runner = tasks.loop(seconds=delay, loop=loop)(self.main)
        self.cache = None
        self.clients = []
        all_listeners.append(self)

    def add_client(self, client: Client) -> None:
        """Add a client to fire events for."""
        if client not in self.clients:
            self.clients.append(client)

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
        """Accurately shutdown a scanner.
        If force is true, cancel the runner, and wait until it finishes otherwise.
        """
        if force:
            self.runner.cancel()
        else:
            self.runner.stop()

    async def on_error(self, exc: Exception) -> None:
        """Basic event handler to print the errors if any occur."""
        traceback.print_exc()

    async def scan(self) -> None:
        """This function should contain main code of the scanner."""
        pass

    async def main(self) -> None:
        """Main function, that is basically doing all the job."""
        try:
            await self.scan()

        except Exception as exc:
            await self.on_error(exc)


class TimelyLevelScanner(AbstractScanner):
    def __init__(
        self, t_type: str, delay: int = 10.0, *,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:
        super().__init__(delay, loop=loop)
        self.method = getattr(scanner_client, 'get_' + t_type)
        self.call_method = 'new_' + t_type

    async def scan(self) -> None:
        """Scan for either daily or weekly levels."""
        timely = await self.method()

        if self.cache is None:
            self.cache = timely
            return

        if timely.id != self.cache.id:
            for client in self.clients:
                dispatcher = client.dispatch(self.call_method, timely)
                self.loop.create_task(dispatcher)  # schedule the execution

        self.cache = timely


class RateLevelScanner(AbstractScanner):
    def __init__(
        self, listen_to_rate: bool = True, delay: float = 10.0,
        *, loop: asyncio.AbstractEventLoop = None
    ) -> None:
        super().__init__(delay, loop=loop)
        self.call_method = 'level_rated' if listen_to_rate else 'level_unrated'
        self.filters = Filters(strategy='awarded')
        self.find_new = listen_to_rate
        self.cache = []

    async def method(self, pages: int = 2) -> List[Level]:
        return await scanner_client.search_levels(filters=self.filters, pages=range(pages))

    async def scan(self) -> None:
        new = await self.method()

        if not self.cache:
            self.cache = new
            return

        difference = differ(self.cache, new, self.find_new)

        self.cache = new

        async for level in further_differ(difference, self.find_new):
            for client in self.clients:
                dispatcher = client.dispatch(self.call_method, level)
                self.loop.create_task(dispatcher)


async def further_differ(
    array: Iterable[Level], find_new: bool = True
) -> AsyncIterator[Level]:
    array = list(array)
    updated = await asyncio.gather(*(level.refresh() for level in array))

    for level, new in zip(array, updated):
        if find_new:
            if new.is_rated() or new.has_coins_verified():
                yield new
        else:
            if new is None:
                yield level
            elif not new.is_rated() and not new.has_coins_verified():
                yield new


def differ(before: list, after: list, find_new: bool = True) -> filter:
    a, b = (before, after) if find_new else (after, before)
    return filter(lambda elem: (elem not in a), b)


daily_listener = TimelyLevelScanner('daily')
weekly_listener = TimelyLevelScanner('weekly')

rate_listener = RateLevelScanner(listen_to_rate=True)
unrate_listener = RateLevelScanner(listen_to_rate=False)
