from typing import Type, TypeVar

from attrs import field, frozen
from typing_extensions import Never

from gd.enums import ByteOrder
from gd.memory.data import Data, USize
from gd.memory.pointers import MutPointer, Pointer
from gd.memory.state import AbstractState
from gd.platform import PlatformConfig

__all__ = ("Ref", "MutRef")

IMMUTABLE_REFERENCE = "the reference is immutable"

T = TypeVar("T")


@frozen()
class Ref(Data[T]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[Pointer[T]] = field(default=Pointer[T])

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> T:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order).value

    def write(
        self,
        state: AbstractState,
        address: int,
        value: T,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> Never:
        raise TypeError(IMMUTABLE_REFERENCE)

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)


@frozen()
class MutRef(Data[T]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[MutPointer[T]] = field(default=MutPointer[T], repr=False)

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> T:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order).value

    def write(
        self,
        state: AbstractState,
        address: int,
        value: T,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        self.internal_pointer_type(
            state, address, self.type, self.pointer_type, order
        ).value = value

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)
