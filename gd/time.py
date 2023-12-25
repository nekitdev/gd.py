from time import perf_counter as default_clock

from attrs import field, frozen
from pendulum import Duration, duration
from typing_aliases import Nullary
from typing_extensions import Self

__all__ = ("Clock", "Timer")

Clock = Nullary[float]
"""Represents clocks that return time in seconds."""


@frozen()
class Timer:
    """Represents timers."""

    clock: Clock = field(default=default_clock)
    created_at: float = field(init=False)

    @created_at.default
    def default_created_at(self) -> float:
        return self.clock()

    def elapsed(self) -> Duration:
        seconds = self.clock() - self.created_at

        return duration(seconds=seconds)

    def reset(self) -> Self:
        return type(self)(self.clock)
