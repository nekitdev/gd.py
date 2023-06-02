from __future__ import annotations

from typing import TYPE_CHECKING, Type
from typing import Union as TypingUnion

from attrs import frozen

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS, EMPTY
from gd.enums import ByteOrder
from gd.memory.arrays import MutArrayData
from gd.memory.base import Struct, Union, UnionData, struct, union
from gd.memory.constants import CONTENT_LENGTH
from gd.memory.data import U8 as Byte
from gd.memory.data import Data, Int, USize
from gd.memory.fields import Field
from gd.memory.pointers import MutPointerData
from gd.memory.utils import next_power_of_two
from gd.platform import PlatformConfig

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("String", "OldString", "StringData")

NULL_BYTE = bytes(1)


@union()
class StringContent(Union):
    inline = Field(MutArrayData(Byte(), CONTENT_LENGTH))
    pointer = Field(MutPointerData(MutArrayData(Byte())))


@struct()
class String(Struct):
    content = Field(UnionData(StringContent))
    length = Field(USize())
    capacity = Field(USize())

    @property
    def value(self) -> str:
        content = self.content
        capacity = self.capacity
        length = self.length

        if capacity < CONTENT_LENGTH:
            try:
                return self.state.read_at(content.inline.address, length).decode(  # optimized
                    DEFAULT_ENCODING, DEFAULT_ERRORS
                )

            except UnicodeDecodeError:
                pass

        try:
            return self.state.read_at(content.pointer.value_address, length).decode(  # optimized
                DEFAULT_ENCODING, DEFAULT_ERRORS
            )

        except UnicodeDecodeError:
            return EMPTY

    @value.setter
    def value(self, value: str) -> None:
        content = self.content
        capacity = self.capacity

        data = value.encode(DEFAULT_ENCODING, DEFAULT_ERRORS)
        length = len(data)

        data += NULL_BYTE
        size = len(data)

        self.length = length

        content_length = CONTENT_LENGTH

        if length > capacity:
            if length < content_length:
                self.capacity = content_length - 1

                self.state.write_at(content.inline.address, data)  # optimized

            else:
                size = next_power_of_two(size)

                address = self.state.allocate(size)

                content.pointer.value_address = address

                self.capacity = size - 1

                self.state.write_at(content.pointer.value_address, data)  # optimized

        else:
            if capacity < content_length:
                self.state.write_at(content.inline.address, data)

            return self.state.write_at(content.pointer.value_address, data)


@struct()
class OldStringData(Struct):
    length = Field(USize())
    capacity = Field(USize())
    ref_count = Field(Int())


@struct()
class OldString(Struct):
    pointer = Field(MutPointerData(MutArrayData(Byte())))

    @property
    def string_data(self) -> OldStringData:
        state = self.state
        order = self.order

        old_string_data = OldStringData.reconstruct_for(state)

        address = self.pointer.value_address

        offset = old_string_data.SIZE

        return old_string_data(state, address - offset, order)

    @property
    def value(self) -> str:
        string_data = self.string_data
        content = self.pointer.value

        try:
            return self.state.read_at(content.address, string_data.length).decode(  # optimized
                DEFAULT_ENCODING, DEFAULT_ERRORS
            )

        except UnicodeDecodeError:
            return EMPTY

    @value.setter
    def value(self, value: str) -> None:
        string_data = self.string_data

        ref_count = string_data.ref_count

        capacity = string_data.capacity

        data = value.encode(DEFAULT_ENCODING, DEFAULT_ERRORS)
        length = len(data)

        data += NULL_BYTE
        size = len(data)

        offset = string_data.SIZE

        if length > capacity:
            size = next_power_of_two(size + offset)

            address = self.state.allocate(size)

            self.pointer.value_address = address + offset

            string_data = self.string_data

            string_data.capacity = size - offset - 1

            string_data.ref_count = ref_count

        string_data.length = length

        self.state.write_at(self.pointer.value.address, data)  # optimized


@frozen()
class StringData(Data[str]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> str:
        return self.compute_type(state.config)(state, address, order).value

    def write(
        self, state: AbstractState, address: int, value: str, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        self.compute_type(state.config)(state, address, order).value = value

    def compute_size(self, config: PlatformConfig) -> int:
        return self.compute_type(config).SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.compute_type(config).ALIGNMENT

    def compute_type(self, config: PlatformConfig) -> TypingUnion[Type[String], Type[OldString]]:
        if config.platform.is_windows():
            return String.reconstruct(config)  # type: ignore

        return OldString.reconstruct(config)  # type: ignore
