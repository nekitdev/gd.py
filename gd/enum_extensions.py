from typing import ClassVar, Set
from enum_extensions import Enum as ExtendedEnum
from enum_extensions import Flag as ExtendedFlag

from enum_extensions import FormatTrait, OrderTrait
from enum_extensions import TitleTrait as ExtendedTitleTrait

__all__ = ("Enum", "Flag", "TitleTrait")

ABBREVIATIONS = {"NA", "UFO", "XL"}


class TitleTrait(ExtendedTitleTrait):
    ABBREVIATIONS: ClassVar[Set[str]] = ABBREVIATIONS


class Enum(FormatTrait, OrderTrait, ExtendedEnum):
    pass


class Flag(FormatTrait, OrderTrait, ExtendedFlag):
    pass
