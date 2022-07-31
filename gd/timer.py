from datetime import datetime, timedelta
from typing import Type, TypeVar, overload

from attrs import field, frozen

__all__ = ("Timer", "create_timer")

T = TypeVar("T", bound="Timer")

clock = datetime.utcnow


@frozen()
class Timer:
    created_at: datetime = field(factory=clock)

    def current(self) -> datetime:
        return clock()

    def elapsed(self) -> timedelta:
        return self.current() - self.created_at


@overload
def create_timer() -> Timer:
    ...


@overload
def create_timer(timer_type: Type[T]) -> T:
    ...


def create_timer(timer_type: Type[Timer] = Timer) -> Timer:
    return timer_type()
