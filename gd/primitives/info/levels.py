from __future__ import annotations

from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING, Self

from attrs import define
from iters.iters import iter

from gd.binary.protocols import Binary
from gd.converters import CONVERTER
from gd.primitives.info.defaults import (
    DEFAULT_LEVEL_AUTO,
    DEFAULT_LEVEL_DAILY,
    DEFAULT_LEVEL_EASY,
    DEFAULT_LEVEL_GAUNTLET,
    DEFAULT_LEVEL_HARD,
    DEFAULT_LEVEL_HARDER,
    DEFAULT_LEVEL_INSANE,
    DEFAULT_LEVEL_NORMAL,
)
from gd.primitives.info.robtop import LEVEL_INFO_SEPARATOR, concat_level_info, split_level_info
from gd.internals.robtop.protocols import RobTop
from gd.schema.core import LevelInfoSchema
from gd.typing import Data

if TYPE_CHECKING:
    from gd.schema.core import LevelInfoBuilder, LevelInfoReader

__all__ = ("LevelInfo", "LevelInfoData")


class LevelInfoData(Data):
    auto: int
    easy: int
    normal: int
    hard: int
    harder: int
    insane: int

    daily: int
    gauntlet: int


@define()
class LevelInfo(Binary, RobTop):
    auto: int = DEFAULT_LEVEL_AUTO
    easy: int = DEFAULT_LEVEL_EASY
    normal: int = DEFAULT_LEVEL_NORMAL
    hard: int = DEFAULT_LEVEL_HARD
    harder: int = DEFAULT_LEVEL_HARDER
    insane: int = DEFAULT_LEVEL_INSANE

    daily: int = DEFAULT_LEVEL_DAILY
    gauntlet: int = DEFAULT_LEVEL_GAUNTLET

    @classmethod
    def from_data(cls, data: LevelInfoData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> LevelInfoData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(LevelInfoSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(LevelInfoSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with LevelInfoSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(LevelInfoSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: LevelInfoReader) -> Self:
        return cls(
            auto=reader.auto,
            easy=reader.easy,
            normal=reader.normal,
            hard=reader.hard,
            harder=reader.harder,
            insane=reader.insane,
            daily=reader.daily,
            gauntlet=reader.gauntlet,
        )

    def to_builder(self) -> LevelInfoBuilder:
        builder = LevelInfoSchema.new_message()

        builder.auto = self.auto
        builder.easy = self.easy
        builder.normal = self.normal
        builder.hard = self.hard
        builder.harder = self.harder
        builder.insane = self.insane

        builder.daily = self.daily
        builder.gauntlet = self.gauntlet

        return builder

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        auto, easy, normal, hard, harder, insane, daily, gauntlet = (
            iter(split_level_info(string)).map(int).tuple()
        )

        return cls(
            auto=auto,
            easy=easy,
            normal=normal,
            hard=hard,
            harder=harder,
            insane=insane,
            daily=daily,
            gauntlet=gauntlet,
        )

    def to_robtop(self) -> str:
        return (
            iter.of(
                self.auto,
                self.easy,
                self.normal,
                self.hard,
                self.harder,
                self.insane,
                self.daily,
                self.gauntlet,
            )
            .map(str)
            .collect(concat_level_info)
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return LEVEL_INFO_SEPARATOR in string
