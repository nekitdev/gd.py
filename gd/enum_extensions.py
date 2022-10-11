from enum_extensions.standard import Enum as ExtendedEnum
from enum_extensions.standard import Flag as ExtendedFlag
from enum_extensions.traits import Format, Order, Title

__all__ = ("Enum", "Flag")

ABBREVIATIONS = {"NA", "UFO", "XL"}

Title.ABBREVIATIONS.update(ABBREVIATIONS)


class Enum(Format, Order, Title, ExtendedEnum):
    pass


class Flag(Enum, ExtendedFlag):
    pass
