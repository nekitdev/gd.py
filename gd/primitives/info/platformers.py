from io import BufferedReader, BufferedWriter
from typing import TYPE_CHECKING

from attrs import define
from iters.iters import iter
from typing_extensions import Self

from gd.binary.protocols import Binary
from gd.converters import CONVERTER
from gd.primitives.info.defaults import (
    DEFAULT_PLATFORMER_AUTO,
    DEFAULT_PLATFORMER_EASY,
    DEFAULT_PLATFORMER_HARD,
    DEFAULT_PLATFORMER_HARDER,
    DEFAULT_PLATFORMER_INSANE,
    DEFAULT_PLATFORMER_NORMAL,
)
from gd.primitives.info.robtop import (
    PLATFORMER_INFO_SEPARATOR,
    concat_platformer_info,
    split_platformer_info,
)
from gd.internals.robtop.protocols import RobTop
from gd.schema.core import PlatformerInfoSchema
from gd.typing import Data

if TYPE_CHECKING:
    from gd.schema.core import PlatformerInfoBuilder, PlatformerInfoReader

__all__ = ("PlatformerInfo", "PlatformerInfoData")


class PlatformerInfoData(Data):
    auto: int
    easy: int
    normal: int
    hard: int
    harder: int
    insane: int


@define()
class PlatformerInfo(Binary, RobTop):
    auto: int = DEFAULT_PLATFORMER_AUTO
    easy: int = DEFAULT_PLATFORMER_EASY
    normal: int = DEFAULT_PLATFORMER_NORMAL
    hard: int = DEFAULT_PLATFORMER_HARD
    harder: int = DEFAULT_PLATFORMER_HARDER
    insane: int = DEFAULT_PLATFORMER_INSANE

    @classmethod
    def from_data(cls, data: PlatformerInfoData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> PlatformerInfoData:
        return CONVERTER.unstructure(self)  # type: ignore[no-any-return]

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(PlatformerInfoSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(PlatformerInfoSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with PlatformerInfoSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(PlatformerInfoSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: PlatformerInfoReader) -> Self:
        return cls(
            auto=reader.auto,
            easy=reader.easy,
            normal=reader.normal,
            hard=reader.hard,
            harder=reader.harder,
            insane=reader.insane,
        )

    def to_builder(self) -> PlatformerInfoBuilder:
        builder = PlatformerInfoSchema.new_message()

        builder.auto = self.auto
        builder.easy = self.easy
        builder.normal = self.normal
        builder.hard = self.hard
        builder.harder = self.harder
        builder.insane = self.insane

        return builder

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        auto, easy, normal, hard, harder, insane = (
            iter(split_platformer_info(string)).map(int).tuple()
        )

        return cls(auto=auto, easy=easy, normal=normal, hard=hard, harder=harder, insane=insane)

    def to_robtop(self) -> str:
        return (
            iter.of(self.auto, self.easy, self.normal, self.hard, self.harder, self.insane)
            .map(str)
            .collect(concat_platformer_info)
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return PLATFORMER_INFO_SEPARATOR in string
