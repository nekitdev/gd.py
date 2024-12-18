from attrs import frozen
from iters.iters import iter
from typing_extensions import Self

from gd.defaults.primitives.colors import DEFAULT_BLUE, DEFAULT_GREEN, DEFAULT_RED
from gd.internals.robtop.core import concat_iterable_with, split_iterable_with
from gd.internals.robtop.protocols import RobTop

COLOR_SEPARATOR = ","
"""The separator used in color strings."""

split_color = split_iterable_with(COLOR_SEPARATOR)
concat_color = concat_iterable_with(COLOR_SEPARATOR)


@frozen()
class InternalColor(RobTop):
    """Represents colors internally."""

    red: int = DEFAULT_RED
    """The red value of the color."""

    green: int = DEFAULT_GREEN
    """The green value of the color."""

    blue: int = DEFAULT_BLUE
    """The blue value of the color."""

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        red, green, blue = iter(split_color(string)).map(int).tuple()

        return cls(red, green, blue)

    def to_robtop(self) -> str:
        return iter.of(self.red, self.green, self.blue).map(str).collect(concat_color)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return COLOR_SEPARATOR in string
