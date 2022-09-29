from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from attrs import define, field

from gd.enums import ByteOrder
from gd.memory.data import USize
from gd.memory.state import AbstractState

if TYPE_CHECKING:
    from gd.memory.data import Data

T = TypeVar("T")

NULL_POINTER = "the pointer is null"

IMMUTABLE_POINTER = "the pointer is immutable"


@define()
class Pointer(Generic[T]):
    state: AbstractState = field()
    address: int = field(repr=hex)
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)
    order: ByteOrder = field(default=ByteOrder.NATIVE)

    @property
    def value_address(self) -> int:
        return self.pointer_type.read(self.state, self.address, self.order)

    @value_address.setter
    def value_address(self, address: int) -> None:
        self.pointer_type.write(self.state, self.address, address, self.order)

    def is_null(self) -> bool:
        return not self.value_address

    @property
    def value(self) -> T:
        value_address = self.value_address

        if not value_address:
            raise ValueError(NULL_POINTER)

        return self.type.read(self.state, value_address, self.order)

    @value.setter
    def value(self, value: T) -> None:
        raise TypeError(IMMUTABLE_POINTER)


@define()
class MutPointer(Pointer[T]):
    @property
    def value(self) -> T:
        value_address = self.value_address

        if not value_address:
            raise ValueError(NULL_POINTER)

        return self.type.read(self.state, value_address, self.order)

    @value.setter
    def value(self, value: T) -> None:
        value_address = self.value_address

        if not value_address:
            raise ValueError(NULL_POINTER)

        self.type.write(self.state, value_address, value, self.order)
