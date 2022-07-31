from abc import abstractmethod
from typing import Any, Type, TypeVar

from typing_extensions import Protocol, TypeGuard, runtime_checkable

from gd.typing import is_instance

__all__ = ("String", "FromString", "ToString", "is_from_string", "is_to_string")

S = TypeVar("S", bound="FromString")


@runtime_checkable
class FromString(Protocol):
    @classmethod
    @abstractmethod
    def from_string(cls: Type[S], string: str) -> S:
        ...


def is_from_string(item: Any) -> TypeGuard[FromString]:
    return is_instance(item, FromString)


@runtime_checkable
class ToString(Protocol):
    @abstractmethod
    def to_string(self) -> str:
        ...


def is_to_string(item: Any) -> TypeGuard[ToString]:
    return is_instance(item, ToString)


@runtime_checkable
class String(FromString, ToString, Protocol):
    pass
