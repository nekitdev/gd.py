from abc import abstractmethod as required
from typing import Any, Protocol, TypeVar, runtime_checkable

from typing_aliases import is_instance
from typing_extensions import Self, TypeGuard

__all__ = ("RobTop", "FromRobTop", "ToRobTop", "is_from_robtop", "is_to_robtop")

T = TypeVar("T", bound="FromRobTop")


@runtime_checkable
class FromRobTop(Protocol):
    @classmethod
    @required
    def from_robtop(cls, string: str) -> Self:
        ...

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return False


def is_from_robtop(item: Any) -> TypeGuard[FromRobTop]:
    return is_instance(item, FromRobTop)


@runtime_checkable
class ToRobTop(Protocol):
    @required
    def to_robtop(self) -> str:
        ...


def is_to_robtop(item: Any) -> TypeGuard[ToRobTop]:
    return is_instance(item, ToRobTop)


@runtime_checkable
class RobTop(FromRobTop, ToRobTop, Protocol):
    pass
