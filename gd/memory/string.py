"""
# type: ignore

from itertools import count

import iters

from gd.decorators import cache_by
from gd.memory.marker import Struct, Union, mut_array, mut_pointer, char_t, int_t, uintsize_t
from gd.memory.memory_array import MemoryArray
from gd.memory.memory_base import MemoryStruct
from gd.memory.types import Types
from gd.platform import Platform
from gd.typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ()

CONTENT_SIZE = 0x10
EMPTY_STRING = ""
NULL_BYTE = bytes(1)


def array_to_bytes(array: MemoryArray[int], length: int) -> bytes:
    return bytes(iters.iter(array).take(length).unwrap())


def closest_power_of(base: int, value: int) -> int:
    for power in count():
        close = base ** power

        if close >= value:
            return close


class msvc_std_string_content(Union):
    inline: mut_array(char_t, CONTENT_SIZE)
    pointer: mut_pointer(mut_array(char_t))


class msvc_std_string(Struct):
    content: msvc_std_string_content
    length: uintsize_t
    capacity: uintsize_t

    def get_value(self) -> str:
        content = self.content
        length = self.length

        if length < content.size:
            try:
                return array_to_bytes(content.inline, length).decode()

            except UnicodeDecodeError:
                pass

        try:
            return array_to_bytes(content.pointer.value, length).decode()

        except (RuntimeError, UnicodeDecodeError):  # null pointer or can not decode
            return EMPTY_STRING

    def set_value(self, value: str) -> None:
        content = self.content
        capacity = self.capacity

        data = value.encode()
        length = len(data)

        data += NULL_BYTE
        size = len(data)

        self.length = length

        if length < content.size:
            return content.inline.write(data)

        if length > capacity:
            size = closest_power_of(2, size)

            address = self.state.allocate_at(0, size)

            self.capacity = size - 1

            content.pointer.value_address = address

        return content.pointer.value.write(data)

    value = property(get_value, set_value)

    # XXX: should this be here?

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> str:
        string = cls(state, address)

        return string.value

    def write(self, state: "BaseState", address: int) -> None:
        ...

    @classmethod
    def write_value_to(cls, value: str, state: "BaseState", address: int) -> None:
        string = cls(state, address)

        string.value = value


class std_string_info(Struct):
    capacity: uintsize_t
    length: uintsize_t
    ref_count: int_t


class std_string(Struct):
    pointer: mut_pointer(mut_array(char_t))

    @property
    @cache_by("bits", "platform")
    def info_struct(self) -> Type[MemoryStruct]:
        return std_string_info.create(self.bits, self.platform)

    @property
    def info(self) -> MemoryStruct:
        info_struct = self.info_struct

        return info_struct(self.state, self.pointer.value_address - info_struct.size)

    def get_value(self) -> str:
        return array_to_bytes(self.pointer.value, self.info.length).decode()

    def set_value(self, value: str) -> None:
        info_struct = self.info_struct
        info = self.info

        capacity = info.capacity
        ref_count = info.ref_count

        data = value.encode()
        length = len(data)

        data += NULL_BYTE
        size = len(data)

        if length > capacity:
            size = closest_power_of(2, size)

            address = self.state.allocate_at(0, size + info_struct.size)

            info = info_struct(self.state, address)

            info.capacity = size - 1
            info.ref_count = ref_count

            address += info_struct.size

            self.pointer.value_address = address

        info.length = length

        return self.pointer.value.write(data)

    value = property(get_value, set_value)

    # XXX: should this be here?

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> str:
        string = cls(state, address)

        return string.value

    def write(self, state: "BaseState", address: int) -> None:
        ...

    @classmethod
    def write_value_to(cls, value: str, state: "BaseState", address: int) -> None:
        string = cls(state, address)

        string.value = value


@Types.register_function
def string_t(bits: int, platform: Platform) -> Type[MemoryStruct]:
    if platform is Platform.WINDOWS:
        return msvc_std_string.create(bits, platform)

    return std_string.create(bits, platform)

"""
