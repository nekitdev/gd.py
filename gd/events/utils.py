import asyncio
import atexit
import threading

from gd import tasks
from gd.events.listener import all_listeners, get_loop, run_loop, set_loop, shutdown_loop
from gd.typing import List, Optional

__all__ = (
    "attach_to_loop",
    "cancel_tasks",
    "disable",
    "enable",
    "run",
    "shutdown_loops",
    "shutdown_threads",
    "start",
)

# these are used internally
_current_thread = 1
_loops: List[asyncio.AbstractEventLoop] = []
_tasks: List[tasks.Loop] = []
_threads: List[threading.Thread] = []


def cancel_tasks() -> None:
    """Cancel all running task-loop objects."""
    for task in _tasks:
        try:
            task.cancel()
        except Exception:  # noqa
            pass  # uwu

    _tasks.clear()


def shutdown_loops() -> None:
    """Shutdown all loops used for event listening."""
    for loop in _loops:
        try:
            shutdown_loop(loop)

        except Exception:  # noqa
            pass  # sorry

    _loops.clear()


def shutdown_threads() -> None:
    """Join all threads (should be daemon). Call this function after shutting loops down."""
    for thread in _threads:
        thread.join()

    _threads.clear()


def disable() -> None:
    """Shorthand for calling all three functions:

    .. code-block:: python3

        gd.events.cancel_tasks()
        gd.events.shutdown_loops()
        gd.events.shutdown_threads()

    This function is intended to be called at the end of programs, and is also run on shutdown.
    """
    cancel_tasks()
    shutdown_loops()
    shutdown_threads()


def enable(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Attach all listeners to the ``loop``. If not provided, default loop is used."""
    if loop is None:
        loop = get_loop()

    if getattr(loop, "gd_event_running", False):
        return

    _loops.append(loop)

    for listener in all_listeners:
        task = tasks.loop(seconds=listener.delay, loop=loop)(listener.main)

        _tasks.append(task)

        task.start()

    loop.gd_event_running = True  # type: ignore


def attach_to_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Set ``loop`` as default loop in gd.events."""
    set_loop(loop)


def run(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Run listeners in a given loop."""
    if loop is None:
        loop = get_loop()

    enable(loop)

    try:
        run_loop(loop)
    except KeyboardInterrupt:
        pass


def start(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Does the same as :func:`.run`, but in the remote thread."""
    global _current_thread

    thread = threading.Thread(
        target=run, args=(loop,), name=f"ListenerThread-{_current_thread}", daemon=True
    )

    _current_thread += 1
    _threads.append(thread)

    thread.start()


atexit.register(disable)
