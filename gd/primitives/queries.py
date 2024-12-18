from typing import Iterable, Type, TypeVar

from attrs import frozen
from iters.iters import iter
from typing_aliases import DynamicTuple
from typing_extensions import Self

from gd.converters import CONVERTER
from gd.internals.primitives.queries import InternalQuery
from gd.typing import IntString

__all__ = ("EMPTY_QUERY", "QueryPart", "QueryParts", "Query", "query")

QueryPart = IntString
QueryParts = DynamicTuple[QueryPart]


def parse_query_part(string: str) -> QueryPart:
    try:
        return int(string)

    except ValueError:
        return string


@frozen()
class Query:
    parts: QueryParts = ()

    @classmethod
    def from_iterable(cls, iterable: Iterable[QueryPart]) -> Self:
        return cls.from_parts(tuple(iterable))

    @classmethod
    def of(cls, *parts: QueryPart) -> Self:
        return cls.from_parts(parts)

    @classmethod
    def from_parts(cls, parts: QueryParts) -> Self:
        return cls(parts)

    def into_parts(self) -> QueryParts:
        return self.parts

    @classmethod
    def from_internal(cls, internal: InternalQuery) -> Self:
        return iter(internal.parts).map(parse_query_part).collect(cls.from_iterable)

    def into_internal(self) -> InternalQuery:
        return iter(self.parts).map(str).collect(InternalQuery.from_iterable)


def query(*parts: QueryPart) -> Query:
    return Query(parts)


EMPTY_QUERY = query()


def unstructure_query(query: Query) -> QueryParts:
    return query.into_parts()


Q = TypeVar("Q", bound=Query)


def structure_query(parts: QueryParts, query_type: Type[Q]) -> Q:
    return query_type.from_parts(parts)


CONVERTER.register_structure_hook(Query, structure_query)
CONVERTER.register_unstructure_hook(Query, unstructure_query)
