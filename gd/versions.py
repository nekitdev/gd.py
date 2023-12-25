from __future__ import annotations

from attrs import Attribute, field, frozen
from typing_extensions import Self
from typing_extensions import TypedDict as Data

from gd.converter import CONVERTER
from gd.robtop import RobTop
from gd.simple import Simple
from gd.string_utils import is_digit

__all__ = (
    "CURRENT_GAME_VERSION",
    "CURRENT_BINARY_VERSION",
    "RobTopVersion",
    "RobTopVersionData",
    "GameVersion",
)

BASE = 10

DEFAULT_MAJOR = 0
DEFAULT_MINOR = 0

EXPECTED_MAJOR = "expected `major >= 0`"
EXPECTED_MINOR = "expected `minor >= 0`"
EXPECTED_BASE = f"expected `minor < {BASE}`"

VERSION = "{}.{}"
version = VERSION.format


class RobTopVersionData(Data):
    major: int
    minor: int


@frozen(order=True)
class RobTopVersion(RobTop, Simple[int]):
    major: int = field(default=DEFAULT_MAJOR)
    minor: int = field(default=DEFAULT_MINOR)

    def __hash__(self) -> int:
        return self.to_value()

    def __str__(self) -> str:
        return version(self.major, self.minor)

    @major.validator
    def check_major(self, attribute: Attribute[int], major: int) -> None:
        if major < 0:
            raise ValueError(EXPECTED_MAJOR)

    @minor.validator
    def check_minor(self, attribute: Attribute[int], minor: int) -> None:
        if minor < 0:
            raise ValueError(EXPECTED_MINOR)

        if minor >= BASE:
            raise ValueError(EXPECTED_BASE)

    @classmethod
    def from_data(cls, data: RobTopVersionData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> RobTopVersionData:
        return CONVERTER.unstructure(self)  # type: ignore

    @classmethod
    def from_value(cls, value: int) -> Self:
        major, minor = divmod(value, BASE)

        return cls(major, minor)

    def to_value(self) -> int:
        return self.major * BASE + self.minor

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return cls.from_value(int(string))

    def to_robtop(self) -> str:
        return str(self.to_value())

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return is_digit(string)


INVALID_GAME_VERSION = "invalid game version: `{}`"
invalid_game_version = INVALID_GAME_VERSION.format


@frozen()
class GameVersion(RobTopVersion):
    @classmethod
    def from_robtop_value(cls, value: int) -> Self:  # why...
        if not value:
            return cls()

        if 0 < value < 8:
            return cls(1, value - 1)

        if value < 10:
            raise ValueError(INVALID_GAME_VERSION.format(value))

        if value == 10:
            return cls(1, 7)

        if value == 11:
            return cls(1, 8)

        return cls.from_value(value)

    def to_robtop_value(self) -> int:  # whyyy...
        major = self.major
        minor = self.minor

        if major == 1:
            if minor == 8:
                return 11

            elif minor == 7:
                return 10

            elif minor < 7:
                return minor + 1

        return self.to_value()

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        return cls.from_robtop_value(int(string))

    def to_robtop(self) -> str:
        return str(self.to_robtop_value())


CURRENT_GAME_VERSION = GameVersion(2, 2)
CURRENT_BINARY_VERSION = RobTopVersion(3, 8)
