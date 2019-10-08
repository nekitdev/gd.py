import asyncio
import threading
import signal
import logging

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
        self._closed = False
        self._running = False
        self.delay = delay
        self.future = None
        self.cache = None
        self.clients = []
        self.init_loop()

    def is_closed(self):
        return self._closed

    def add_client(self, client):
        """Add a client to fire events for."""
        if client not in self.clients:
            self.clients.append(client)

    def run(self):
        """Run a scanner. In idea, this should be called from another thread."""
        loop = self.loop

        asyncio.set_event_loop(loop)

        def stop_loop_on_completion(future):
            self.close()

        self.future = asyncio.ensure_future(self.main(), loop=loop)
        self.future.add_done_callback(stop_loop_on_completion)

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            log.info('Received the signal to terminate the event loop.')

        finally:
            self.future.remove_done_callback(stop_loop_on_completion)
            log.info('Cleaning up tasks.')

            self.close()

    def init_loop(self):
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, self.close)
            loop.add_signal_handler(signal.SIGTERM, self.close)
        except NotImplementedError:
            pass

    def start(self):
        """Start a scanner."""
        if not self._running:
            self._running = True
            self.thread.start()

    def close(self, *args):
        """Accurately shutdown a scanner."""
        if not self.is_closed():
            self._closed = True

            if self.future is not None:
                self.future.cancel()

            self.shutdown_loop(self.loop)

            if self.thread.is_alive():
                self.thread.join()

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

    async def scan(self):
        """This function should contain main code of the scanner."""
        pass

    async def on_error(self):
        """An event that is called if an error occurs while scanning."""
        pass

    async def main(self):
        """Main function, that is basically doing all the job."""
        while not self.is_closed():

            try:
                await self.scan()

            except asyncio.CancelledError:
                pass

            except Exception:
                await self.on_error()

            await asyncio.sleep(self.delay)


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

        if timely.id != self.cache.id and self.clients:
            await utils.wait(getattr(client, self.call_method)() for client in self.clients)

        self.cache = timely


daily_listener = TimelyLevelScanner('daily')
weekly_listener = TimelyLevelScanner('weekly')

all_listeners = [daily_listener, weekly_listener]
