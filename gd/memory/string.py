# DOCUMENT; TODO: IMPROVE OPTIMIZATION

# type: ignore

# from itertools import islice as iter_slice

from gd.memory.marker import Struct, Union, mut_array, mut_pointer, char_t, intsize_t, uintsize_t
# from gd.memory.memory_array import MemoryArray
from gd.memory.memory_base import MemoryStruct
from gd.memory.types import types
from gd.memory.utils import closest_power_of_two
from gd.platform import Platform
from gd.typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("old_std_string", "std_string")

CONTENT_SIZE = 0x10
EMPTY_STRING = ""
NULL_BYTE = bytes(1)


# def to_bytes(array: MemoryArray[int], length: int) -> bytes:
#     return bytes(iter_slice(array, length))


class std_string_content(Union):
    inline: mut_array(char_t, CONTENT_SIZE)
    pointer: mut_pointer(mut_array(char_t))


class std_string(Struct):
    content: std_string_content
    length: uintsize_t
    capacity: uintsize_t

    def get_value(self) -> str:
        content = self.content
        capacity = self.capacity
        length = self.length

        if capacity < content.size:
            try:
                # return to_bytes(content.inline, length).decode()  # <- optimization required

                return self.state.read_at(content.inline.address, length).decode()  # optimized

            except UnicodeDecodeError:
                pass

        try:
            # return to_bytes(content.pointer.value, length).decode()  # <- optimization required

            return self.state.read_at(content.pointer.value_address, length).decode()  # optimized

        except UnicodeDecodeError:
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

                # return content.inline.write(data)  # <- optimization required

                self.state.write_at(content.inline.address, data)  # optimized

            else:
                size = closest_power_of_two(size)

                address = self.state.allocate(size)

                content.pointer.value_address = address

                self.capacity = size - 1

                # return content.pointer.value.write(data)  # <- optimization required

                self.state.write_at(content.pointer.value_address, data)  # optimized

        else:
            if capacity < content.size:
                return content.inline.write(data)

            return content.pointer.value.write(data)

    value = property(get_value, set_value)

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


class old_std_long_string(Struct, origin=3):
    capacity: uintsize_t
    length: uintsize_t
    ref_count: intsize_t

    content: mut_array(char_t)  # <- origin


class old_std_string(Struct):
    pointer: mut_pointer(old_std_long_string)

    def get_value(self) -> str:
        long_string = self.pointer.value

        try:
            # return to_bytes(  # <- optimization required
            #     long_string.content, long_string.length
            # ).decode()

            return self.state.read_at(long_string.content.address, long_string.length)  # optimized

        except UnicodeDecodeError:
            return EMPTY_STRING

    def set_value(self, value: str) -> None:
        long_string = self.pointer.value

        ref_count = long_string.ref_count

        capacity = long_string.capacity

        data = value.encode()
        length = len(data)

        data += NULL_BYTE
        size = len(data)

        if length > capacity:
            size = closest_power_of_two(size + long_string.size)

            address = self.state.allocate(size)

            self.pointer.value_address = address + long_string.size

            long_string = self.pointer.value

            long_string.capacity = size - long_string.size - 1

            long_string.ref_count = ref_count

        long_string.length = length

        # return long_string.content.write(data)  # <- optimization required

        self.state.write_at(long_string.content.address, data)  # optimized

    value = property(get_value, set_value)

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


@types.register_function
def string_t(bits: int, platform: Platform) -> Type[MemoryStruct]:
    # XXX: on later versions of std libraries the struct used is std_string

    if platform is Platform.WINDOWS:
        return std_string.create(bits, platform)

    return old_std_string.create(bits, platform)
