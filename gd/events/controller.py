from asyncio import AbstractEventLoop, new_event_loop, set_event_loop
from signal import SIGINT, SIGTERM
from threading import Thread
from typing import Iterable, Optional

from attrs import define, field
from typing_aliases import DynamicTuple, NormalError

from gd.asyncio import shutdown_loop
from gd.events.listeners import Listener

CONTROLLER_NOT_RUNNING = "the controller is not running"
CONTROLLER_ALREADY_STARTED = "the controller has already started"

Listeners = DynamicTuple[Listener]
ListenerIterable = Iterable[Listener]


def convert_listeners(iterable: ListenerIterable) -> Listeners:
    return tuple(iterable)


@define()
class Controller:
    listeners: Listeners = field(default=(), converter=convert_listeners)

    loop: AbstractEventLoop = field(factory=new_event_loop)

    _thread: Optional[Thread] = field(default=None, init=False)

    def run(self) -> None:
        loop = self.loop

        try:
            loop.add_signal_handler(SIGINT, loop.stop)
            loop.add_signal_handler(SIGTERM, loop.stop)

        except RuntimeError:
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

        except NormalError:
            pass  # uwu

    def start(self) -> None:
        thread = self._thread

        if thread is not None:
            raise RuntimeError(CONTROLLER_ALREADY_STARTED)

        self._thread = thread = Thread(target=self.run, daemon=True)

        thread.start()

    def stop(self) -> None:
        thread = self._thread

        if thread is None:
            raise RuntimeError(CONTROLLER_NOT_RUNNING)

        loop = self.loop

        loop.call_soon_threadsafe(shutdown_loop, loop)

        thread.join()

        self._thread = None
