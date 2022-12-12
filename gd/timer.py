from datetime import timedelta as duration
from time import perf_counter as clock
from typing import Type, TypeVar, overload

from attrs import field, frozen

__all__ = ("Timer", "create_timer")

T = TypeVar("T", bound="Timer")


@frozen()
class Timer:
    created_at: float = field(factory=clock)

    def current(self) -> float:
        return clock()

    def elapsed(self) -> duration:
        return duration(seconds=self.current() - self.created_at)


@overload
def create_timer() -> Timer:
    ...


@overload
def create_timer(timer_type: Type[T]) -> T:
    ...


def create_timer(timer_type: Type[Timer] = Timer) -> Timer:
    return timer_type()
