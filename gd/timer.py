from time import perf_counter as clock
from typing import Type, TypeVar, overload

from attrs import field, frozen
from pendulum import Duration, duration

__all__ = ("Timer", "now")

T = TypeVar("T", bound="Timer")


@frozen()
class Timer:
    created_at: float = field(factory=clock)

    def current(self) -> float:
        return clock()

    def elapsed(self) -> Duration:
        return duration(seconds=self.current() - self.created_at)

    def reset(self: T) -> T:
        return type(self)()


@overload
def now() -> Timer:
    ...


@overload
def now(timer_type: Type[T]) -> T:
    ...


def now(timer_type: Type[Timer] = Timer) -> Timer:
    return timer_type()
