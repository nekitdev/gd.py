import ctypes

from gd.text_utils import make_repr
from gd.typing import Any, Sequence, Union

__all__ = ("Buffer",)

EMPTY_BYTES = bytes(0)

_bytes_from_hex = bytes.fromhex


def _bytes_to_hex(data: bytes, step: int = 1) -> str:
    return " ".join(data[index : index + step].hex() for index in range(0, len(data), step))


class BufferMeta(type):
    def __getitem__(cls, item: Union[int, Sequence[int]]) -> "Buffer":
        if isinstance(item, Sequence):
            return cls.from_byte_array(item)

        return cls.from_byte_array([item])

    def from_byte_array(cls, array: Sequence[int]) -> "Buffer":
        raise NotImplementedError("This function is implemented in the actual class.")


class Buffer(metaclass=BufferMeta):
    def __init__(self, data: bytes = EMPTY_BYTES) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.to_hex().upper()

    def __repr__(self) -> str:
        info = {"data": repr(self.to_hex().upper())}
        return make_repr(self, info)

    @property
    def data(self) -> bytes:
        return self._data

    @classmethod
    def from_byte_array(cls, array: Sequence[int]) -> "Buffer":
        return cls(bytes(array))

    def to_byte_array(self) -> Sequence[int]:
        return list(self.data)

    @classmethod
    def from_hex(cls, hex_string: str) -> "Buffer":
        return cls(_bytes_from_hex(hex_string))

    def to_hex(self, step: int = 1) -> str:
        return _bytes_to_hex(self._data, step)

    def into_buffer(self) -> Any:
        return ctypes.create_string_buffer(self.data, len(self.data))

    def into(self) -> bytes:
        return self.data
