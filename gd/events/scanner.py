import asyncio
import threading
import signal
import logging
import traceback

from ..client import Client

from .. import utils

__all__ = (
    'AbstractScanner', 'TimelyLevelScanner',
    'daily_listener', 'weekly_listener'
)

scanner_client = Client(loop=asyncio.new_event_loop())

log = logging.getLogger(__name__)


class AbstractScanner:
    def __init__(self, delay: float = 10.0):
        self.thread = threading.Thread(target=self.run, name=self.__class__.__name__+'Thread')
        self.loop = asyncio.new_event_loop()
        self.runner = utils.tasks.loop(seconds=10.0)(self.main)
        self.runner.change_interval(seconds=delay)
        self.cache = None
        self.clients = []
        self.init_loop()

    def add_client(self, client):
        """Add a client to fire events for."""
        if client not in self.clients:
            self.clients.append(client)

    def attach_to_loop(self, loop):
        """Attach the runner to another event loop."""
        self.runner.loop = loop
        try:
            self.runner.start()
        except RuntimeError:
            pass

    @utils.run_once
    def run(self):
        """Run a scanner. In idea, this should be called from another thread."""
        self.attach_to_loop(self.loop)

        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_forever()

        except KeyboardInterrupt:
            log.info('Received the signal to terminate the event loop.')

        finally:
            log.info('Cleaning up tasks.')
            self.close()

    def init_loop(self):
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, self.close)
            loop.add_signal_handler(signal.SIGTERM, self.close)
        except NotImplementedError:
            pass

    @utils.run_once
    def start(self):
        """Start a scanner."""
        self.thread.start()

    @utils.run_once
    def close(self, *args, force: bool = True):
        """Accurately shutdown a scanner.
        If force is true, cancel the runner, and wait until it finishes otherwise.
        """
        if force:
            self.runner.cancel()
        else:
            self.runner.stop()

        self.shutdown_loop(self.loop)

        try:
            self.thread.join()
        except RuntimeError:
            pass

    def shutdown_loop(self, loop):
        """Shutdown a loop."""
        def shutdown(loop):
            loop.call_soon_threadsafe(loop.stop)

            try:
                tasks = asyncio.all_tasks(loop)
            except AttributeError:
                tasks = asyncio.Task.all_tasks(loop)

            for task in tasks:
                task.cancel()

        shutdown(loop)

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
