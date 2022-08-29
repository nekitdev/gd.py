from typing import Type

from typing_extensions import TypeAlias

from gd.constants import DEFAULT_ENCODING
from gd.memory.fields import mut_field
from gd.memory.markers import Struct, Union, char_t, intsize_t, mut_array, mut_pointer, uintsize_t
from gd.memory.types import types
from gd.memory.utils import closest_power_of_two
from gd.platform import PlatformConfig

__all__ = ("old_string", "string")

CONTENT_SIZE = 0x10
NULL_BYTE = bytes(1)


inline_content: TypeAlias = mut_array(char_t, CONTENT_SIZE)
content_pointer: TypeAlias = mut_pointer(mut_array(char_t))


class string_content(Union):
    inline: inline_content = mut_field()
    pointer: content_pointer = mut_field()


class string(Struct):
    content: string_content = mut_field()
    length: uintsize_t = mut_field()
    capacity: uintsize_t = mut_field()

    def get_value(self) -> str:
        content = self.content
        capacity = self.capacity
        length = self.length

        if capacity < content.size:
            try:
                return self.state.read_at(content.inline.address, length).decode(DEFAULT_ENCODING)

            except UnicodeDecodeError:
                pass

        return self.state.read_at(content.pointer.value_address, length).decode(DEFAULT_ENCODING)

    def set_value(self, value: str) -> None:
        content = self.content
        capacity = self.capacity

        data = value.encode(DEFAULT_ENCODING)
        length = len(data)

        data += NULL_BYTE
        size = len(data)

        self.length = length

        if length > capacity:
            if length < content.size:
                self.capacity = content.size - 1

                self.state.write_at(content.inline.address, data)

            else:
                size = closest_power_of_two(size)

                address = self.state.allocate(size)

                content.pointer.value_address = address

                self.capacity = size - 1

                self.state.write_at(content.pointer.value_address, data)

        else:
            if capacity < content.size:
                return content.inline.write(data)

            return content.pointer.value.write(data)

    value = property(get_value, set_value)

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> str:
        string = cls(state, address)

        return string.value

    @classmethod
    def write_value_to(cls, value: str, state: "BaseState", address: int) -> None:
        string = cls(state, address)

        string.value = value


content: TypeAlias = mut_array(char_t)


class old_long_string(Struct, origin=3):
    capacity: uintsize_t
    length: uintsize_t
    ref_count: intsize_t

    content: content  # <- origin


old_long_string_pointer: TypeAlias = mut_pointer(old_long_string)


class old_string(Struct):
    pointer: old_long_string_pointer

    def get_value(self) -> str:
        long_string = self.pointer.value

        return self.state.read_at(long_string.content.address, long_string.length).decode(
            DEFAULT_ENCODING
        )

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

        self.state.write_at(long_string.content.address, data)

    value = property(get_value, set_value)

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> str:
        string = cls(state, address)

        return string.value

    @classmethod
    def write_value_to(cls, value: str, state: "BaseState", address: int) -> None:
        string = cls(state, address)

        string.value = value


@types.register_function
def string_t(config: PlatformConfig) -> Type[Struct]:
    if config.platform.is_windows():
        return string

    return old_string
