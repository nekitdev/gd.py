import asyncio
import threading
import signal
import logging
import traceback

from ..client import Client

from .. import utils

__all__ = (
    'AbstractScanner', 'TimelyLevelScanner',
    'daily_listener', 'weekly_listener', 'run'
)

loop = asyncio.new_event_loop()

scanner_client = Client(loop=loop)

log = logging.getLogger(__name__)


def shutdown_loop(loop):
    """Shutdown a loop."""
    loop.call_soon_threadsafe(loop.stop)

    try:
        tasks = asyncio.all_tasks(loop)
    except AttributeError:
        tasks = asyncio.Task.all_tasks(loop)

    for task in tasks:
        task.cancel()

    try:
        loop.call_soon_threadsafe(loop.close)
    except RuntimeError:
        pass


def run(loop):
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


thread = threading.Thread(target=run, args=(loop,), name='ScannerThread')


class AbstractScanner:
    def __init__(self, delay: float = 10.0):
        self.runner = utils.tasks.loop(seconds=delay, loop=loop)(self.main)
        self.cache = None
        self.clients = []

    def add_client(self, client):
        """Add a client to fire events for."""
        if client not in self.clients:
            self.clients.append(client)

    def attach_to_loop(self, loop):
        """Attach the runner to another event loop."""
        self.runner.loop = loop

    def enable(self):
        try:
            self.runner.start()
        except RuntimeError:
            pass

    @utils.run_once
    def close(self, *args, force: bool = True):
        """Accurately shutdown a scanner.
        If force is true, cancel the runner, and wait until it finishes otherwise.
        """
        if force:
            self.runner.cancel()
        else:
            self.runner.stop()

    async def on_error(self, exc):
        """Basic event handler to print the errors if any occur."""
        traceback.print_exc()

    async def scan(self):
        """This function should contain main code of the scanner."""
        pass

    async def main(self):
        """Main function, that is basically doing all the job."""
        try:
            await self.scan()

        except Exception as exc:
            await self.on_error(exc)


class TimelyLevelScanner(AbstractScanner):
    def __init__(self, t_type: str):
        super().__init__()
        self.type = t_type
        self.method = getattr(scanner_client, 'get_' + t_type)
        self.call_method = 'on_new_' + t_type

    async def scan(self):
        """Scan for either daily or weekly levels."""
        timely = await self.method()

        if self.cache is None:
            self.cache = timely
            return

        if (timely.id != self.cache.id) and self.clients:
            fs = [getattr(client, self.call_method)(timely) for client in self.clients]
            await utils.wait(fs)

        self.cache = timely


daily_listener = TimelyLevelScanner('daily')
weekly_listener = TimelyLevelScanner('weekly')

all_listeners = [daily_listener, weekly_listener]
