from asyncio import AbstractEventLoop, new_event_loop, set_event_loop
from signal import SIGINT, SIGTERM
from threading import Thread
from typing import Optional

from attrs import define, field

from gd.async_utils import shutdown_loop
from gd.events.listeners import Listener
from gd.typing import DynamicTuple

CONTROLLER_NOT_RUNNING = "the controller is not running"
CONTROLLER_ALREADY_STARTED = "the controller has already started"


@define()
class Controller:
    listeners: DynamicTuple[Listener] = field(default=())

    loop: AbstractEventLoop = field(factory=new_event_loop)

    _thread: Optional[Thread] = field(default=None, init=False)

    def run(self) -> None:
        loop = self.loop

        try:
            loop.add_signal_handler(SIGINT, loop.stop)
            loop.add_signal_handler(SIGTERM, loop.stop)

        except (NotImplementedError, RuntimeError):
            pass

        set_event_loop(loop)

        for listener in self.listeners:
            listener.start()

        try:
            loop.run_forever()

        except KeyboardInterrupt:
            pass

        try:
            shutdown_loop(loop)

        except Exception:
            pass  # uwu

    def start(self) -> None:
        thread = self._thread

        if thread is not None:
            raise RuntimeError(CONTROLLER_ALREADY_STARTED)

        self._thread = thread = Thread(target=self.run, daemon=True)

        thread.start()

    def stop(self, stop_loop: int = True) -> None:
        thread = self._thread

        if thread is None:
            raise RuntimeError(CONTROLLER_NOT_RUNNING)

        loop = self.loop

        if stop_loop:
            loop.stop()

        loop.call_soon_threadsafe(shutdown_loop, loop)

        thread.join()

        self._thread = None
