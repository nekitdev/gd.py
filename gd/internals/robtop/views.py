from typing import Generic, Mapping, TypeVar, final

from attrs import frozen
from wraps.primitives.option import NULL, Option, Some

__all__ = ("RobTopView", "StringRobTopView")

K = TypeVar("K")
V = TypeVar("V")


@final
@frozen()
class RobTopView(Generic[K, V]):
    """Represents RobTop views over mappings."""

    mapping: Mapping[K, V]
    """The mapping to view into."""

    def get_option(self, key: K) -> Option[V]:
        """Similar to `get`, but returns [`Option[V]`][wraps.option.Option]
        instead of [`Optional[V]`][typing.Optional].

        Arguments:
            key: The key to get the value for.

        Returns:
            [`Some(value)`][wraps.option.Some] if the key is present,
                otherwise [`NULL`][wraps.option.NULL].
        """
        mapping = self.mapping

        return Some(mapping[key]) if key in mapping else NULL


T = TypeVar("T")

StringRobTopView = RobTopView[str, T]
"""Represents RobTop views over string mappings."""
