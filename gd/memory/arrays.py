from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional, Sequence, TypeVar

from attrs import define, field

from gd.enums import ByteOrder
from gd.memory.state import AbstractState

if TYPE_CHECKING:
    from gd.memory.fields import Field

__all__ = ("Array",)

T = TypeVar("T")

UNSIZED_ARRAY = "array is unsized"
NEGATIVE_INDEX = "expected non-negative index"
OUT_OF_BOUNDS_INDEX = "index is out-of-bounds"


@define()
class Array(Sequence[T]):
    """Represents `array` types."""

    state: AbstractState = field()
    address: int = field(repr=hex)
    type: Field[T] = field()
    length: Optional[int] = field(default=None)
    order: ByteOrder = field(default=ByteOrder.NATIVE)

    def read_at(self, index: int) -> T:
        if index < 0:
            raise ValueError(NEGATIVE_INDEX)

        length = self.length

        if length is not None and index >= length:
            raise ValueError(OUT_OF_BOUNDS_INDEX)

        state = self.state
        order = self.order

        type = self.type

        size = type.compute_size(state.config)

        return type.read(state, self.address + size * index, order)

    def iter(self) -> Iterator[T]:
        state = self.state
        order = self.order

        type = self.type

        size = type.compute_size(state.config)

        address = self.address

        length = self.length

        if length is None:
            while True:
                yield type.read(state, address, order)

                address += size

        else:
            for _ in range(length):
                yield type.read(state, address, order)

                address += size

    def __getitem__(self, index: int) -> T:
        return self.read_at(index)

    def __len__(self) -> int:
        length = self.length

        if length is None:
            raise TypeError(UNSIZED_ARRAY)

        return length

    def __iter__(self) -> Iterator[T]:
        return self.iter()


@define()
class MutArray(Array[T]):
    def write_at(self, index: int, value: T) -> None:
        if index < 0:
            raise ValueError(NEGATIVE_INDEX)

        length = self.length

        if length is not None and index >= length:
            raise ValueError(OUT_OF_BOUNDS_INDEX)

        state = self.state
        order = self.order

        type = self.type

        size = type.compute_size(state.config)

        type.write(state, self.address + size * index, value, order)

    def __setitem__(self, index: int, value: T) -> None:
        self.write_at(index, value)
