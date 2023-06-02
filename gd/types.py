from typing import Any, TypeVar, Union

from solus import Singleton
from typing_extensions import TypeGuard

__all__ = ("NoDefault", "NoDefaultOr", "is_no_default", "is_not_no_default")


class NoDefault(Singleton):
    """Represents the absence of default values."""


no_default = NoDefault()
"""The instance of [`NoDefault`][gd.types.NoDefault]."""


T = TypeVar("T")

NoDefaultOr = Union[NoDefault, T]


def is_no_default(item: Any) -> TypeGuard[NoDefault]:
    return item is no_default


def is_not_no_default(item: NoDefaultOr[T]) -> TypeGuard[T]:
    return item is not no_default
