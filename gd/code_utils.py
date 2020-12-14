import inspect
import pdb
import sys
from datetime import datetime, timedelta
from types import FrameType

from gd.typing import Any, Callable, NoReturn, Optional, Tuple, TypeVar

__all__ = (
    "TimerWithElapsed",
    "breakpoint",
    "get_frame",
    "print_source",
    "time_execution",
    "time_execution_and_print",
    "unimplemented",
    "unreachable",
)

T = TypeVar("T")


class TimerWithElapsed:
    """Simple timer that keeps track of when it was created."""

    def __init__(self) -> None:
        self.created_at = self.get_current()

    def get_current(self) -> datetime:
        return datetime.utcnow()

    def elapsed(self) -> timedelta:
        return self.get_current() - self.created_at


get_frame = getattr(sys, "_getframe", None)

if get_frame is None:

    class GetFrame(Exception):
        pass

    def get_frame(level: int = 0) -> FrameType:
        try:
            raise GetFrame()

        except GetFrame as error:
            traceback = error.__traceback__

            if traceback is None:
                raise ValueError("No traceback to get the frame from.")

            current_frame = traceback.tb_frame

            if current_frame is None:
                raise ValueError("Can not get current frame.")

            frame = current_frame.f_back

            if frame is None:
                raise ValueError("Can not get caller frame.")

            if level:
                for _ in range(level):
                    frame = frame.f_back

                    if frame is None:
                        raise ValueError("Call stack is not deep enough.") from None

            return frame


def breakpoint(message: Optional[str] = None, *, prompt: str = "(dbg) ") -> None:
    """Drop into the debugger at the call site."""
    debugger = pdb.Pdb()

    debugger.prompt = prompt

    if message is not None:
        debugger.message(message)

    frame = get_frame()

    if frame is not None:
        debugger.set_trace(frame.f_back)

        del frame


def print_source(some_object: Any) -> None:
    """Attempt to find and print source of the object, and do nothing on fail."""
    try:
        print(inspect.getsource(some_object))

    except Exception:
        pass


def time_execution(function: Callable[..., T], *args, **kwargs) -> Tuple[T, timedelta]:
    r"""Execute given ``function`` with ``args`` and ``kwargs`` and measure elapsed time.

    Parameters
    ----------
    function: Callable[..., ``T``]
        Function to call.

    \*args
        Arguments to call function with.

    \*\*kwargs
        Keyword arguments to call function with.

    Returns
    -------
    Tuple[``T``, :class:`datetime.timedelta`]
        Tuple: result of the ``function`` and time elapsed.
    """
    timer = TimerWithElapsed()

    result = function(*args, **kwargs)

    return result, timer.elapsed()


def time_execution_and_print(function: Callable[..., T], *args, **kwargs) -> T:
    r"""Execute given ``function`` with ``args`` and ``kwargs`` and print elapsed time.

    Prints a message like ``Executed function_name in 0:00:00.001000``.

    Parameters
    ----------
    function: Callable[..., ``T``]
        Function to call.

    \*args
        Arguments to call function with.

    \*\*kwargs
        Keyword arguments to call function with.

    Returns
    -------
    ``T``
        Result that the ``function`` returns.
    """
    result, elapsed = time_execution(function, *args, **kwargs)

    name = getattr(function, "__qualname__", repr(function))

    print(f"Executed {name} in {elapsed}.")

    return result


def unimplemented(*args, **kwargs) -> NoReturn:
    """Indicates that the code is unimplemented.

    Raises
    ------
    :exc:`NotImplementedError`
        Error that is raised when this function is called.
    """
    raise NotImplementedError("Function that was called is not implemented.")


def unreachable() -> NoReturn:
    """Indicates the code that is unreachable.

    Raises
    ------
    :exc:`RuntimeError`
        Error that is raised when, for some reason, this function is called.
    """
    raise RuntimeError("Reached code marked as unreachable.")
