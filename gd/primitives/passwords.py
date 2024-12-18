from __future__ import annotations

from typing import Optional, Type, TypeVar

from attrs import frozen
from typing_extensions import Self

from gd.enums.passwords import PasswordType
from gd.internals.primitives.passwords import InternalPassword

__all__ = ("NO_PASSWORD", "Password")

NOT_COPYABLE = "not copyable"

COPYABLE_NO_PASSWORD = "copyable, no password"

COPYABLE_WITH_PASSWORD = "copyable, password `{}`"
copyable_with_password = COPYABLE_WITH_PASSWORD.format

NO_PASSWORD = ~0
"""Represents levels that can be copied without passwords."""


@frozen()
class Password:
    """Represents passwords."""

    optional: Optional[int] = None
    """The optional password value.

    If [`None`], the level is not copyable.
    If [`NO_PASSWORD`][gd.primitives.passwords.NO_PASSWORD], the level is copyable with no password.
    Otherwise, the level is copyable with the password corresponding to the [`int`][int] value.
    """

    @classmethod
    def from_internal(cls, internal: InternalPassword) -> Self:
        return cls(internal.optional)

    def into_internal(self) -> InternalPassword:
        return InternalPassword(self.optional)

    @property
    def type(self) -> PasswordType:
        optional = self.optional

        if optional is None:
            return PasswordType.NOT_COPYABLE

        if optional == NO_PASSWORD:
            return PasswordType.COPYABLE_NO_PASSWORD

        return PasswordType.COPYABLE_WITH_PASSWORD

    @classmethod
    def from_optional(cls, optional: Optional[int]) -> Self:
        return cls(optional)

    def into_optional(self) -> Optional[int]:
        return self.optional

    def __str__(self) -> str:
        optional = self.optional

        if optional is None:
            return NOT_COPYABLE

        if optional == NO_PASSWORD:
            return COPYABLE_NO_PASSWORD

        return copyable_with_password(optional)


def unstructure_password(password: Password) -> Optional[int]:
    return password.into_optional()


P = TypeVar("P", bound=Password)


def structure_password(optional: Optional[int], password_type: Type[P]) -> P:
    return password_type.from_optional(optional)
