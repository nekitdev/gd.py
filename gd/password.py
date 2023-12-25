from __future__ import annotations

from typing import ClassVar, Optional

from attrs import Attribute, define, field
from typing_extensions import Self

from gd.constants import DEFAULT_COPYABLE
from gd.converter import CONVERTER
from gd.encoding import decode_robtop_string, encode_robtop_string
from gd.enums import Key
from gd.robtop import RobTop
from gd.typing import Data

__all__ = ("Password", "PasswordData")

COPYABLE_NO_PASSWORD = "copyable, no password"

COPYABLE_PASSWORD = "copyable, password `{}`"
copyable_password = COPYABLE_PASSWORD.format

NOT_COPYABLE = "not copyable"

NO_PASSWORD = 1


class PasswordData(Data):
    password: Optional[int]
    copyable: bool


@define()
class Password(RobTop):
    ADD: ClassVar[int] = 1_000_000

    value: Optional[int] = field(default=None)
    copyable: bool = field(default=DEFAULT_COPYABLE)

    @value.validator
    def check_value(self, attribute: Attribute[Optional[int]], password: Optional[int]) -> None:
        if password is not None:
            if password >= self.ADD:
                raise ValueError  # TODO: message?

    def __hash__(self) -> int:
        return hash(self.value) ^ self.copyable

    def has_no_password(self) -> bool:
        return self.value is None

    def has_password(self) -> bool:
        return self.value is not None

    def is_copyable(self) -> bool:
        return self.copyable

    @classmethod
    def from_data(cls, data: PasswordData) -> Self:
        return CONVERTER.structure(data, cls)

    def into_data(self) -> PasswordData:
        return CONVERTER.unstructure(self)  # type: ignore

    def __str__(self) -> str:
        if self.is_copyable():
            value = self.value

            if value is None:
                return COPYABLE_NO_PASSWORD

            return copyable_password(value)

        return NOT_COPYABLE

    @classmethod
    def from_robtop_value(cls, value: int) -> Self:
        if not value:
            return cls(value=None, copyable=False)

        if value == NO_PASSWORD:
            return cls(value=None, copyable=True)

        return cls(value=value % cls.ADD, copyable=True)

    def to_robtop_value(self) -> int:
        if self.copyable:
            value = self.value

            if value is None:
                return NO_PASSWORD

            return value + self.ADD

        return 0

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        string = decode_robtop_string(string, Key.LEVEL_PASSWORD)

        if not string:
            value = 0

        else:
            value = int(string)

        return cls.from_robtop_value(value)

    def to_robtop(self) -> str:
        return encode_robtop_string(str(self.to_robtop_value()), Key.LEVEL_LEADERBOARD)

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return True
