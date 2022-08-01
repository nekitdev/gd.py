from __future__ import annotations

from typing import BinaryIO, Type, TypeVar

from attrs import Attribute, field, frozen
from typing_extensions import Final, Literal

from gd.binary import Binary
from gd.binary_utils import U8_SIZE, Reader, Writer, from_u8, to_u8
from gd.enums import ByteOrder
from gd.robtop import RobTop
from gd.string import String
from gd.string_utils import tick

__all__ = ("CURRENT_GAME_VERSION", "CURRENT_BINARY_VERSION", "Version", "GameVersion")

BASE: Final = 10

V = TypeVar("V", bound="Version")


@frozen(eq=True, order=True)
class Version(Binary, String):
    major: int = field(default=0)
    minor: int = field(default=0)

    base: int = field(default=BASE, repr=False)

    @major.validator
    def check_major(self, attribute: Attribute[int], major: int) -> None:
        if major < 0:
            raise ValueError  # TODO: message?

    @minor.validator
    def check_minor(self, attribute: Attribute[int], minor: int) -> None:
        if minor < 0:
            raise ValueError  # TODO: message?

        if minor >= self.base:
            raise ValueError  # TODO: message?

    @classmethod
    def from_value(cls: Type[V], value: int, base: int = BASE) -> V:
        major, minor = divmod(value, base)

        return cls(major, minor, base)

    def to_value(self) -> int:
        return self.major * self.base + self.minor

    @classmethod
    def from_string(cls: Type[V], string: str, base: int = BASE) -> V:
        return cls.from_value(int(string), base)

    def to_string(self) -> str:
        return str(self.to_value())

    # assume `u8` is enough

    @classmethod
    def from_binary(
        cls: Type[V], binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT, base: int = BASE
    ) -> V:
        reader = Reader(binary)

        return cls.from_value(reader.read_u8(order), base)

    def to_binary(self, binary: BinaryIO, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        writer = Writer(binary)

        writer.write_u8(self.to_value(), order)


G = TypeVar("G", bound="GameVersion")

INVALID_GAME_VERSION = "invalid game version: {}"


@frozen()
class GameVersion(RobTop, Version):
    @classmethod
    def from_robtop_value(cls: Type[G], value: int) -> G:
        if not value:
            return cls()

        if 0 < value < 8:
            return cls(1, value - 1)

        if value < 10:
            raise ValueError(INVALID_GAME_VERSION.format(tick(str(value))))

        if value == 10:
            return cls(1, 7)

        if value == 11:
            return cls(1, 8)

        return cls.from_value(value)

    def to_robtop_value(self) -> int:
        major = self.major
        minor = self.minor

        if major == 1:
            if minor == 7:
                return 10

            elif minor < 7:
                return minor + 1

        return self.to_value()

    @classmethod
    def from_robtop(cls: Type[G], string: str) -> G:
        return cls.from_robtop_value(int(string))

    def to_robtop(self) -> str:
        return str(self.to_robtop_value())

    @classmethod
    def can_be_in(cls, string: str) -> Literal[True]:
        return True


CURRENT_GAME_VERSION = GameVersion(2, 1)
CURRENT_BINARY_VERSION = Version(3, 5)
