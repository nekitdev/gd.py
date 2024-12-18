from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING

from attrs import frozen
from typing_extensions import Self

from gd.binary.protocols import Binary
from gd.converters import CONVERTER
from gd.schema.constants import REGULAR
from gd.schema.core import EitherRecordSchema
from gd.typing import Data

if TYPE_CHECKING:
    from gd.schema.core import EitherRecordBuilder, EitherRecordReader

__all__ = ("EitherRecord", "EitherRecordData")

DEFAULT_RECORD = 0
DEFAULT_PLATFORMER = False


class EitherRecordData(Data):
    record: int
    platformer: bool


@frozen()
class EitherRecord(Binary):
    record: int = DEFAULT_RECORD
    platformer: bool = DEFAULT_PLATFORMER

    def is_platformer(self) -> bool:
        return self.platformer

    @classmethod
    def from_data(cls, data: EitherRecordData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> EitherRecordData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(EitherRecordSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(EitherRecordSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with EitherRecordSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(EitherRecordSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: EitherRecordReader) -> Self:
        if reader.which() == REGULAR:
            return cls(record=reader.regular, platformer=False)

        return cls(record=reader.platformer, platformer=True)

    def to_builder(self) -> EitherRecordBuilder:
        builder = EitherRecordSchema.new_message()

        record = self.record

        if self.is_platformer():
            builder.platformer = record

        else:
            builder.regular = record

        return builder
