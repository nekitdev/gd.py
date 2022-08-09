from __future__ import annotations

from abc import abstractmethod
from builtins import hasattr as has_attribute
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Type, TypeVar

from typing_extensions import TypeGuard, runtime_checkable

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = (
    "Layout",
    "Read",
    "ReadWrite",
    "Write",
    "is_layout",
)


class Layout(Protocol):
    size: ClassVar[int]
    alignment: ClassVar[int]


SIZE = "size"
ALIGNMENT = "alignment"


def is_layout(some: Any) -> TypeGuard[Layout]:
    layout = type(some)

    return has_attribute(layout, SIZE) and has_attribute(layout, ALIGNMENT)


T = TypeVar("T")

R = TypeVar("R", covariant=True)


@runtime_checkable
class Read(Layout, Protocol[R]):
    @classmethod
    @abstractmethod
    def read_from(cls: Type[T], state: AbstractState, address: int) -> T:
        ...

    @classmethod
    @abstractmethod
    def read_value_from(cls, state: AbstractState, address: int) -> R:
        ...


W = TypeVar("W", contravariant=True)


@runtime_checkable
class Write(Layout, Protocol[W]):
    def write_to(self, state: AbstractState, address: int) -> None:
        ...

    @classmethod
    def write_value_to(cls, state: AbstractState, value: W, address: int) -> None:
        ...


class ReadWrite(Read[T], Write[T], Protocol[T]):
    pass
