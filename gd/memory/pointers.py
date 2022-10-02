from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Type, TypeVar

from attrs import define, field, frozen

from gd.enums import ByteOrder
from gd.memory.data import Data, USize
from gd.platform import PlatformConfig

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("Pointer", "MutPointer", "PointerData", "MutPointerData")

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


@frozen()
class PointerData(Data[Pointer[T]]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[Pointer[T]] = field(default=Pointer[T], repr=False)

    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> Pointer[T]:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: Pointer[T],
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)


@frozen()
class MutPointerData(Data[MutPointer[T]]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[MutPointer[T]] = field(default=MutPointer[T], repr=False)

    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> MutPointer[T]:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: MutPointer[T],
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)
