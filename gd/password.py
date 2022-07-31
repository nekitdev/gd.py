from __future__ import annotations

from typing import ClassVar, Optional, Type, TypeVar

from attrs import Attribute, define, field

from gd.robtop import RobTop

__all__ = ("Password",)

COPYABLE_NO_PASSWORD = "copyable, no password"
COPYABLE_PASSWORD = "copyable, password {}"
NOT_COPYABLE = "not copyable"

NO_PASSWORD = 1

P = TypeVar("P", bound="Password")


@define()
class Password(RobTop):
    ADD: ClassVar[int] = 1000000

    password: Optional[int] = field(default=None)
    copyable: bool = field(default=False)

    @password.validator
    def check_password(self, attribute: Attribute[Optional[int]], password: Optional[int]) -> None:
        if password:
            if password >= self.ADD:
                raise ValueError  # TODO: message?

    def has_no_password(self) -> bool:
        return self.password is None

    def has_password(self) -> bool:
        return self.password is not None

    def is_copyable(self) -> bool:
        return self.copyable

    def __str__(self) -> str:
        if self.copyable:
            password = self.password

            if password is None:
                return COPYABLE_NO_PASSWORD

            return COPYABLE_PASSWORD.format(password)

        return NOT_COPYABLE

    @classmethod
    def from_robtop_value(cls: Type[P], value: int) -> P:
        if value is None:
            return cls(password=None, copyable=False)

        if value == NO_PASSWORD:
            return cls(password=None, copyable=True)

        return cls(password=value % cls.ADD, copyable=True)

    def to_robtop_value(self) -> int:
        if self.copyable:
            password = self.password

            if password is None:
                return NO_PASSWORD

            return password + self.ADD

        return 0

    @classmethod
    def from_robtop(cls: Type[P], string: str) -> P:
        return cls.from_robtop_value(int(string))

    def to_robtop(self) -> str:
        return str(self.to_robtop_value())
