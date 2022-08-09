from typing import ClassVar, Set

from enum_extensions import Enum as ExtendedEnum
from enum_extensions import Flag as ExtendedFlag
from enum_extensions import Format, Order
from enum_extensions import Title as ExtendedTitle

__all__ = ("Enum", "Flag", "TitleTrait")

ABBREVIATIONS = {"NA", "UFO", "XL"}


class Title(ExtendedTitle):
    ABBREVIATIONS: ClassVar[Set[str]] = ABBREVIATIONS


class Enum(Format, Order, ExtendedEnum):
    pass


class Flag(Format, Order, ExtendedFlag):
    pass
