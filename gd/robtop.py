from abc import abstractmethod as required
from typing import Any, Type, TypeVar

from typing_aliases import is_instance
from typing_extensions import Protocol, TypeGuard, runtime_checkable

__all__ = ("RobTop", "FromRobTop", "ToRobTop", "is_from_robtop", "is_to_robtop")

T = TypeVar("T", bound="FromRobTop")


@runtime_checkable
class FromRobTop(Protocol):
    @classmethod
    @required
    def from_robtop(cls: Type[T], string: str) -> T:
        ...

    @staticmethod
    def can_be_in(string: str) -> bool:
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
