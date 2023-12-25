from typing import Protocol, TypeVar, runtime_checkable

from typing_aliases import required
from typing_extensions import Self

__all__ = ("Simple",)

T = TypeVar("T")


@runtime_checkable
class Simple(Protocol[T]):
    @classmethod
    @required
    def from_value(cls, value: T) -> Self:
        ...

    @required
    def to_value(self) -> T:
        ...
