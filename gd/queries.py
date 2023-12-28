from typing import final

from attrs import frozen
from iters.iters import iter
from typing_aliases import DynamicTuple
from typing_extensions import Self
from gd.models_constants import QUERY_SEPARATOR

from gd.models_utils import concat_query, split_query
from gd.robtop import RobTop
from gd.typing import IntString

__all__ = ("EMPTY_QUERY", "QueryPart", "QueryParts", "Query", "query", "query_parts")

QueryPart = IntString
QueryParts = DynamicTuple[QueryPart]


def parse_query_part(string: str) -> QueryPart:
    try:
        return int(string)

    except ValueError:
        return string


@final
@frozen()
class Query(RobTop):
    parts: QueryParts

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        parts = iter(split_query(string)).map(parse_query_part).tuple()

        return cls(parts)

    def to_robtop(self) -> str:
        return iter(self.parts).map(str).collect(concat_query)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return QUERY_SEPARATOR in string


def query(*parts: QueryPart) -> Query:
    return Query(parts)


def query_parts(parts: QueryParts) -> Query:
    return Query(parts)


EMPTY_QUERY = query()
