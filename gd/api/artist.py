from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING

from attrs import define
from typing_extensions import Self

from gd.binary import Binary
from gd.constants import DEFAULT_ID, EMPTY
from gd.schema import ArtistAPISchema

if TYPE_CHECKING:
    from gd.schema import ArtistAPIBuilder, ArtistAPIReader

__all__ = ("ArtistAPI",)


@define()
class ArtistAPI(Binary):
    id: int
    name: str

    @classmethod
    def default(cls, id: int = DEFAULT_ID, name: str = EMPTY) -> Self:
        return cls(id=id, name=name)

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(ArtistAPISchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(ArtistAPISchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with ArtistAPISchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(ArtistAPISchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: ArtistAPIReader) -> Self:
        return cls(id=reader.id, name=reader.name)

    def to_builder(self) -> ArtistAPIBuilder:
        builder = ArtistAPISchema.new_message()

        builder.id = self.id
        builder.name = self.name

        return builder
