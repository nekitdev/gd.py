from time import monotonic

from attrs import field, frozen
from pendulum import Duration, duration
from typing_aliases import Nullary
from typing_extensions import Self

__all__ = ("Clock", "Timer")

Clock = Nullary[float]
"""Represents functions that return time in seconds."""

default_clock = monotonic
"""The default clock to use."""


@frozen()
class Timer:
    """Represents timers."""

    clock: Clock = field(default=default_clock)
    """The clock to use."""

    created_at: float = field(init=False)
    """The time the timer was created at."""

    @created_at.default
    def default_created_at(self) -> float:
        return self.clock()

    def elapsed(self) -> Duration:
        """Returns the duration since the timer was created.

        Returns:
            The elapsed duration.
        """
        seconds = self.clock() - self.created_at

        return duration(seconds=seconds)

    def reset(self) -> Self:
        """Resets the timer, creating an instance with the same clock.

        Returns:
            The timer created.
        """
        return type(self)(self.clock)
