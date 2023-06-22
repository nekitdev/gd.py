from typing import Iterable, List, TypeVar, Union

from typing_aliases import StringDict, is_instance
from typing_extensions import TypedDict as Data
from typing_extensions import TypeGuard
from yarl import URL

__all__ = (
    "Data",
    "AnyString",
    "IntString",
    "URLString",
    "StrictPrimitive",
    "StrictPayload",
    "MaybeIterable",
    "is_iterable",
)

AnyString = Union[str, bytes]
IntString = Union[int, str]
URLString = Union[URL, str]

StrictPrimitive = Union[bool, int, float, str]
StrictPayload = Union[StrictPrimitive, List["StrictPayload"], StringDict["StrictPayload"]]

T = TypeVar("T")

MaybeIterable = Union[Iterable[T], T]


def is_iterable(maybe_iterable: MaybeIterable[T]) -> TypeGuard[Iterable[T]]:
    return is_instance(maybe_iterable, Iterable)
