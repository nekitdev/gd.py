# DOCUMENT

import ctypes

from gd.typing import Any, Iterator, Sequence, Type, TypeVar, Union

__all__ = ("Buffer", "MutBuffer", "buffer", "mut_buffer")

B = TypeVar("B", bound="Buffer")
MB = TypeVar("MB", bound="MutBuffer")

_concat = " ".join
_from_hex = bytes.fromhex
_hex = bytes.hex


def _slice(data: bytes, step: int = 1) -> Iterator[bytes]:
    for index in range(0, len(data), step):
        yield data[index : index + step]


def _to_hex(data: bytes, step: int = 1) -> str:
    return _concat(map(_hex, _slice(data, step)))


_mut_from_hex = bytearray.fromhex
_mut_hex = bytearray.hex


def _mut_slice(data: bytearray, step: int = 1) -> Iterator[bytearray]:
    for index in range(0, len(data), step):
        yield data[index : index + step]


def _mut_to_hex(data: bytearray, step: int = 1) -> str:
    return _concat(map(_mut_hex, _mut_slice(data, step)))


class BufferType(type):
    def __getitem__(cls: Type[B], item: Union[int, Sequence[int]]) -> B:  # type: ignore
        if isinstance(item, Sequence):
            return cls.from_byte_array(item)

        return cls.from_byte_array([item])

    def from_byte_array(cls: Type[B], array: Sequence[int]) -> B:  # type: ignore
        raise NotImplementedError("This function is implemented in the actual class.")


class BufferBase(metaclass=BufferType):
    pass


class Buffer(BufferBase, bytes):
    def __str__(self) -> str:
        return self.to_hex().upper()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.to_hex().upper()}]>"

    @classmethod
    def from_byte_array(cls: Type[B], array: Sequence[int]) -> B:
        return cls(array)

    def to_byte_array(self) -> Sequence[int]:
        return list(self)

    @classmethod
    def from_hex(cls: Type[B], hex_string: str) -> B:
        return cls(_from_hex(hex_string))

    def to_hex(self, step: int = 1) -> str:
        return _to_hex(self, step)

    def into(self) -> Any:
        return ctypes.create_string_buffer(self, len(self))


class MutBuffer(BufferBase, bytearray):
    def __str__(self) -> str:
        return self.to_hex().upper()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.to_hex().upper()}]>"

    @classmethod
    def from_byte_array(cls: Type[MB], array: Sequence[int]) -> MB:
        return cls(array)

    def to_byte_array(self) -> Sequence[int]:
        return list(self)

    @classmethod
    def from_hex(cls: Type[MB], hex_string: str) -> MB:
        return cls(_mut_from_hex(hex_string))

    def to_hex(self, step: int = 1) -> str:
        return _mut_to_hex(self, step)

    def into(self) -> Any:
        return ctypes.create_string_buffer(self, len(self))


buffer = Buffer
mut_buffer = MutBuffer
