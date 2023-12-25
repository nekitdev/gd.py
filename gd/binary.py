from io import BufferedReader, BufferedWriter
from typing import Protocol, runtime_checkable

from typing_aliases import required
from typing_extensions import Self

__all__ = ("FromBinary", "ToBinary", "Binary")


@runtime_checkable
class FromBinary(Protocol):
    @classmethod
    @required
    def from_binary(cls, binary: BufferedReader) -> Self:
        ...

    @classmethod
    @required
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        ...

    @classmethod
    @required
    def from_bytes(cls, data: bytes) -> Self:
        ...

    @classmethod
    @required
    def from_bytes_packed(cls, data: bytes) -> Self:
        ...


@runtime_checkable
class ToBinary(Protocol):
    @required
    def to_binary(self, binary: BufferedWriter) -> None:
        ...

    @required
    def to_binary_packed(self, binary: BufferedWriter) -> None:
        ...

    @required
    def to_bytes(self) -> bytes:
        ...

    @required
    def to_bytes_packed(self) -> bytes:
        ...


@runtime_checkable
class Binary(FromBinary, ToBinary, Protocol):
    pass
