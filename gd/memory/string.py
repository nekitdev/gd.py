# type: ignore

import iters

from gd.memory.array import MemoryArray
from gd.memory.base import MemoryStruct
from gd.memory.marker import Struct, Union, mut_array, mut_pointer, char_t, uintsize_t
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


class windows_std_string_content(Union):
    inline: mut_array(char_t, CONTENT_SIZE)
    pointer: mut_pointer(mut_array(char_t))


class windows_std_string(Struct, packed=True):
    content: windows_std_string_content
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

        if length >= capacity:
            address = self.state.allocate_at(0, size)

            self.capacity = size

            content.pointer.value_address = address

        return content.pointer.value.write(data)

    value = property(get_value, set_value)

    # XXX: should this be here?

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> str:
        string = cls(state, address)

        return string.value

    @classmethod
    def write_value_to(cls, value: str, state: "BaseState", address: int) -> None:
        string = cls(state, address)

        string.value = value


@Types.register_function
def string_t(bits: int, platform: Platform) -> Type[MemoryStruct]:
    if platform is Platform.WINDOWS:
        return windows_std_string.create(bits, platform)

    raise NotImplementedError(
        f"Implementation of string for {platform.name.casefold()} was not found."
    )
