from __future__ import annotations
from io import BufferedReader, BufferedWriter

from typing import TYPE_CHECKING, ClassVar, Optional

from attrs import Attribute, define, field
from typing_extensions import Self
from gd.binary import Binary

from gd.constants import DEFAULT_COPYABLE
from gd.converter import CONVERTER
from gd.encoding import decode_robtop_string, encode_robtop_string
from gd.enums import Key
from gd.robtop import RobTop
from gd.schema import PasswordSchema
from gd.schema_constants import NONE
from gd.typing import Data

if TYPE_CHECKING:
    from gd.schema import PasswordBuilder, PasswordReader

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
class Password(Binary, RobTop):
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

    @classmethod
    def from_binary(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(PasswordSchema.read(binary))

    @classmethod
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        return cls.from_reader(PasswordSchema.read_packed(binary))

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        with PasswordSchema.from_bytes(data) as reader:
            return cls.from_reader(reader)

    @classmethod
    def from_bytes_packed(cls, data: bytes) -> Self:
        return cls.from_reader(PasswordSchema.from_bytes_packed(data))

    def to_binary(self, binary: BufferedWriter) -> None:
        self.to_builder().write(binary)

    def to_binary_packed(self, binary: BufferedWriter) -> None:
        self.to_builder().write_packed(binary)

    def to_bytes(self) -> bytes:
        return self.to_builder().to_bytes()

    def to_bytes_packed(self) -> bytes:
        return self.to_builder().to_bytes_packed()

    @classmethod
    def from_reader(cls, reader: PasswordReader) -> Self:
        option = reader.value

        if option.which() == NONE:
            value = None

        else:
            value = option.some

        copyable = reader.copyable

        return cls(value=value, copyable=copyable)

    def to_builder(self) -> PasswordBuilder:
        builder = PasswordSchema.new_message()

        value = self.value

        if value is None:
            builder.value.none = None

        else:
            builder.value.some = value

        builder.copyable = self.is_copyable()

        return builder
