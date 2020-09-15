from datetime import datetime, timedelta
import inspect
import pdb

from gd.typing import Any, Callable, NoReturn, Optional, Tuple, TypeVar

__all__ = (
    "TimerWithElapsed",
    "breakpoint",
    "print_source",
    "time_execution",
    "time_execution_and_print",
    "unreachable",
)

T = TypeVar("T")


class TimerWithElapsed:
    def __init__(self) -> None:
        self.created_at = self.get_current()

    def get_current(self) -> datetime:
        return datetime.utcnow()

    def elapsed(self) -> timedelta:
        return self.get_current() - self.created_at


def breakpoint(message: Optional[str] = None, *, prompt: str = "(dbg) ") -> None:
    debugger = pdb.Pdb()

    debugger.prompt = prompt

    if message is not None:
        debugger.message(message)

    frame = inspect.currentframe()

    if frame is not None:
        debugger.set_trace(frame.f_back)

        del frame


def print_source(some_object: Any) -> None:
    try:
        print(inspect.getsource(some_object))
    except Exception:
        pass


def time_execution(function: Callable[..., T], *args, **kwargs) -> Tuple[T, timedelta]:
    timer = TimerWithElapsed()

    result = function(*args, **kwargs)

    return result, timer.elapsed()


def time_execution_and_print(function: Callable[..., T], *args, **kwargs) -> T:
    result, elapsed = time_execution(function, *args, **kwargs)

    name = getattr(function, "__qualname__", repr(function))

    print(f"Executed {name} in {elapsed}.")

    return result


def unreachable() -> NoReturn:
    raise RuntimeError("Reached code marked as unreachable.")
