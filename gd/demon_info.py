from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from iters.iters import iter
from typing_extensions import Self

from gd.binary import Binary
from gd.constants import (
    DEFAULT_DEMON_EASY,
    DEFAULT_DEMON_EXTREME,
    DEFAULT_DEMON_GAUNTLET,
    DEFAULT_DEMON_HARD,
    DEFAULT_DEMON_INSANE,
    DEFAULT_DEMON_MEDIUM,
    DEFAULT_DEMON_WEEKLY,
)
from gd.converter import CONVERTER
from gd.models_constants import DEMON_INFO_SEPARATOR
from gd.models_utils import concat_demon_info, split_demon_info
from gd.robtop import RobTop
from gd.schema import DemonInfoGroupSchema, DemonInfoSchema, DemonInfoSpecialSchema
from gd.typing import Data

if TYPE_CHECKING:
    from io import BufferedReader, BufferedWriter

    from gd.schema import (
        DemonInfoBuilder,
        DemonInfoGroupBuilder,
        DemonInfoGroupReader,
        DemonInfoReader,
        DemonInfoSpecialBuilder,
        DemonInfoSpecialReader,
    )

__all__ = ("DemonInfo", "DemonInfoGroup", "DemonInfoSpecial")


class DemonInfoGroupData(Data):
    easy: int
    medium: int
    hard: int
    insane: int
    extreme: int


@define()
class DemonInfoGroup(Binary):
    easy: int = DEFAULT_DEMON_EASY
    medium: int = DEFAULT_DEMON_MEDIUM
    hard: int = DEFAULT_DEMON_HARD
    insane: int = DEFAULT_DEMON_INSANE
    extreme: int = DEFAULT_DEMON_EXTREME

    @classmethod
    def from_data(cls, data: DemonInfoGroupData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> DemonInfoGroupData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(DemonInfoGroupSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(DemonInfoGroupSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with DemonInfoGroupSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(DemonInfoGroupSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: DemonInfoGroupReader) -> Self:
        return cls(
            easy=reader.easy,
            medium=reader.medium,
            hard=reader.hard,
            insane=reader.insane,
            extreme=reader.extreme,
        )

    def to_builder(self) -> DemonInfoGroupBuilder:
        builder = DemonInfoGroupSchema.new_message()

        builder.easy = self.easy
        builder.medium = self.medium
        builder.hard = self.hard
        builder.insane = self.insane
        builder.extreme = self.extreme

        return builder


class DemonInfoSpecialData(Data):
    weekly: int
    gauntlet: int


@define()
class DemonInfoSpecial(Binary):
    weekly: int = DEFAULT_DEMON_WEEKLY
    gauntlet: int = DEFAULT_DEMON_GAUNTLET

    @classmethod
    def from_data(cls, data: DemonInfoSpecialData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> DemonInfoSpecialData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(DemonInfoSpecialSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(DemonInfoSpecialSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with DemonInfoSpecialSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(DemonInfoSpecialSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: DemonInfoSpecialReader) -> Self:
        return cls(weekly=reader.weekly, gauntlet=reader.gauntlet)

    def to_builder(self) -> DemonInfoSpecialBuilder:
        builder = DemonInfoSpecialSchema.new_message()

        builder.weekly = self.weekly
        builder.gauntlet = self.gauntlet

        return builder


class DemonInfoData(Data):
    regular: DemonInfoGroupData
    platformer: DemonInfoGroupData
    special: DemonInfoSpecialData


@define()
class DemonInfo(Binary, RobTop):
    regular: DemonInfoGroup = field(factory=DemonInfoGroup)
    platformer: DemonInfoGroup = field(factory=DemonInfoGroup)
    special: DemonInfoSpecial = field(factory=DemonInfoSpecial)

    @classmethod
    def from_data(cls, data: DemonInfoData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> DemonInfoData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(DemonInfoSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(DemonInfoSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with DemonInfoSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(DemonInfoSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: DemonInfoReader) -> Self:
        return cls(
            regular=DemonInfoGroup.from_reader(reader.regular),
            platformer=DemonInfoGroup.from_reader(reader.platformer),
            special=DemonInfoSpecial.from_reader(reader.special),
        )

    def to_builder(self) -> DemonInfoBuilder:
        builder = DemonInfoSchema.new_message()

        builder.regular = self.regular.to_builder()
        builder.platformer = self.platformer.to_builder()
        builder.special = self.special.to_builder()

        return builder

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        (
            regular_easy,
            regular_medium,
            regular_hard,
            regular_insane,
            regular_extreme,
            platformer_easy,
            platformer_medium,
            platformer_hard,
            platformer_insane,
            platformer_extreme,
            weekly,
            gauntlet,
        ) = iter(split_demon_info(string)).map(int).tuple()

        return cls(
            regular=DemonInfoGroup(
                easy=regular_easy,
                medium=regular_medium,
                hard=regular_hard,
                insane=regular_insane,
                extreme=regular_extreme,
            ),
            platformer=DemonInfoGroup(
                easy=platformer_easy,
                medium=platformer_medium,
                hard=platformer_hard,
                insane=platformer_insane,
                extreme=platformer_extreme,
            ),
            special=DemonInfoSpecial(weekly=weekly, gauntlet=gauntlet),
        )

    def to_robtop(self) -> str:
        regular = self.regular
        platformer = self.platformer
        special = self.special

        return iter.of(
            str(regular.easy),
            str(regular.medium),
            str(regular.hard),
            str(regular.insane),
            str(regular.extreme),
            str(platformer.easy),
            str(platformer.medium),
            str(platformer.hard),
            str(platformer.insane),
            str(platformer.extreme),
            str(special.weekly),
            str(special.gauntlet),
        ).collect(concat_demon_info)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return DEMON_INFO_SEPARATOR in string
