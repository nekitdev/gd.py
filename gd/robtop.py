from abc import abstractmethod
from typing import Any, Type, TypeVar

from typing_extensions import Protocol, TypeGuard, runtime_checkable

from gd.typing import is_instance

__all__ = ("RobTop", "FromRobTop", "ToRobTop", "is_from_robtop", "is_to_robtop")

F = TypeVar("F", bound="FromRobTop")


@runtime_checkable
class FromRobTop(Protocol):
    @classmethod
    @abstractmethod
    def from_robtop(cls: Type[F], string: str) -> F:
        ...

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return False


def is_from_robtop(item: Any) -> TypeGuard[FromRobTop]:
    return is_instance(item, FromRobTop)


@runtime_checkable
class ToRobTop(Protocol):
    @abstractmethod
    def to_robtop(self) -> str:
        ...


def is_to_robtop(item: Any) -> TypeGuard[ToRobTop]:
    return is_instance(item, ToRobTop)


@runtime_checkable
class RobTop(FromRobTop, ToRobTop, Protocol):
    pass
