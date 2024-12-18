from typing import Iterable

from attrs import frozen
from typing_aliases import DynamicTuple
from typing_extensions import Self

from gd.internals.robtop.core import concat_iterable_with, split_iterable_with
from gd.internals.robtop.protocols import RobTop

QUERY_SEPARATOR = ","
"""The separator used in query strings."""

split_query = split_iterable_with(QUERY_SEPARATOR)
concat_query = concat_iterable_with(QUERY_SEPARATOR)

InternalQueryParts = DynamicTuple[str]
"""[`InternalQuery`][gd.internals.primitives.queries.InternalQuery] parts."""


@frozen()
class InternalQuery(RobTop):
    """Represents queries internally."""

    parts: InternalQueryParts = ()
    """The parts of the query."""

    @classmethod
    def from_iterable(cls, iterable: Iterable[str]) -> Self:
        return cls(tuple(iterable))

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return cls.from_iterable(split_query(string))

    def to_robtop(self) -> str:
        return concat_query(self.parts)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUERY_SEPARATOR in string
