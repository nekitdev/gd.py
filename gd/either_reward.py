from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import frozen
from typing_extensions import Self

from gd.binary import Binary
from gd.constants import DEFAULT_COUNT
from gd.converter import CONVERTER
from gd.schema import EitherRewardSchema
from gd.schema_constants import STARS
from gd.typing import Data

if TYPE_CHECKING:
    from io import BufferedReader, BufferedWriter

    from gd.schema import EitherRewardBuilder, EitherRewardReader


class EitherRewardData(Data):
    count: int
    moons: bool


DEFAULT_MOONS = False


@frozen()
class EitherReward(Binary):
    count: int = DEFAULT_COUNT
    moons: bool = DEFAULT_MOONS

    def is_stars(self) -> bool:
        return not self.moons

    def is_moons(self) -> bool:
        return self.moons

    @classmethod
    def from_data(cls, data: EitherRewardData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> EitherRewardData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(EitherRewardSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(EitherRewardSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with EitherRewardSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(EitherRewardSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: EitherRewardReader) -> Self:
        if reader.which() == STARS:
            return cls(count=reader.stars, moons=False)

        return cls(count=reader.moons, moons=True)

    def to_builder(self) -> EitherRewardBuilder:
        builder = EitherRewardSchema.new_message()

        count = self.count

        if self.is_moons():
            builder.moons = count

        else:
            builder.stars = count

        return builder
