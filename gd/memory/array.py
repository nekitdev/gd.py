from __future__ import annotations

from typing import Iterator, Optional, Sequence, TypeVar

from attrs import define, field

from gd.enums import ByteOrder
from gd.memory.state import AbstractState

__all__ = ("Array",)

T = TypeVar("T")

UNSIZED_ARRAY = "array is unsized"
NEGATIVE_INDEX = "expected non-negative index"


@define()
class Array(Sequence[T]):
    """Represents `array` types."""

    state: AbstractState = field()
    address: int = field(repr=hex)
    type: Field[T] = field()
    length: Optional[int] = field(default=None)
    order: ByteOrder = field(default=ByteOrder.NATIVE)

    def at(self, index: int) -> T:
        if index < 0:
            raise ValueError(NEGATIVE_INDEX)

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
        return self.at(index)

    def __len__(self) -> int:
        length = self.length

        if length is None:
            raise TypeError(UNSIZED_ARRAY)

        return length

    def __iter__(self) -> Iterator[T]:
        return self.iter()


from gd.memory.fields import Field
