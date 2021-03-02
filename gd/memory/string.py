# type: ignore

from itertools import islice as iter_slice

from gd.memory.marker import Struct, Union, mut_array, mut_pointer, char_t, int_t, uintsize_t
from gd.memory.memory_array import MemoryArray
from gd.memory.memory_base import MemoryStruct
from gd.memory.types import Types
from gd.platform import Platform
from gd.typing import TYPE_CHECKING, Callable, Type

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ()

CONTENT_SIZE = 0x10
EMPTY_STRING = ""
NULL_BYTE = bytes(1)


def to_bytes(array: MemoryArray[int], length: int) -> bytes:
    return bytes(iter_slice(array, length))


def closest_power_of_two(value: int) -> Callable[[int], int]:
    result = 1

    while result < value:
        result *= 2

    return result


class msvc_std_string_content(Union):
    inline: mut_array(char_t, CONTENT_SIZE)
    pointer: mut_pointer(mut_array(char_t))


class msvc_std_string(Struct):
    content: msvc_std_string_content
    length: uintsize_t
    capacity: uintsize_t

    def get_value(self) -> str:
        content = self.content
        capacity = self.capacity
        length = self.length

        if capacity < content.size:
            try:
                return to_bytes(content.inline, length).decode()

            except UnicodeDecodeError:
                pass

        try:
            return to_bytes(content.pointer.value, length).decode()

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

        if length > capacity:
            if length < content.size:
                self.capacity = content.size - 1

                return content.inline.write(data)

            else:
                size = closest_power_of_two(size)

                address = self.state.allocate_at(0, size)

                content.pointer.value_address = address

                self.capacity = size - 1

                return content.pointer.value.write(data)

        else:
            if capacity < content.size:
                return content.inline.write(data)

            return content.pointer.value.write(data)

    value = property(get_value, set_value)

    """
    # XXX: should this be here?

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> str:
        string = cls(state, address)

        return string.value

    def write_to(self, state: "BaseState", address: int) -> None:
        ...

    @classmethod
    def write_value_to(cls, value: str, state: "BaseState", address: int) -> None:
        string = cls(state, address)

        string.value = value
    """


class std_string_info(Struct):
    capacity: uintsize_t
    length: uintsize_t
    ref_count: int_t


class std_string(Struct):
    pointer: mut_pointer(mut_array(char_t))


@Types.register_function
def string_t(bits: int, platform: Platform) -> Type[MemoryStruct]:
    if platform is Platform.WINDOWS:
        return msvc_std_string.create(bits, platform)

    return std_string.create(bits, platform)
