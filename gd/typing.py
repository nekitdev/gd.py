from typing import Iterable, TypeVar, Union

from typing_aliases import is_instance
from typing_extensions import TypedDict as Data
from typing_extensions import TypeGuard
from yarl import URL

__all__ = ("Data", "AnyString", "IntString", "URLString", "MaybeIterable", "is_iterable")

AnyString = Union[str, bytes]
IntString = Union[int, str]
URLString = Union[URL, str]

T = TypeVar("T")

MaybeIterable = Union[Iterable[T], T]


def is_iterable(maybe_iterable: MaybeIterable[T]) -> TypeGuard[Iterable[T]]:
    return is_instance(maybe_iterable, Iterable)
