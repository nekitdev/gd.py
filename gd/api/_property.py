"""Automatic object property code generator."""

from enums import Enum

from gd.typing import Union

from gd.api.enums import (
    ColorChannelProperties,
    LevelDataEnum,
    LevelHeaderEnum,
    ObjectDataEnum,
    PlayerColor,
)
from gd.api.parser import (  # type: ignore
    _INT,
    _BOOL,
    _FLOAT,
    _HSV,
    _ENUMS,
    _TEXT,
    _GROUPS,
    _COLOR_INT,
    _COLOR_BOOL,
    _COLOR_PLAYER,
    _COLOR_FLOAT,
    _COLOR_HSV,
    _HEADER_INT,
    _HEADER_BOOL,
    _HEADER_FLOAT,
    _HEADER_COLORS,
    _COLORS,
    _GUIDELINES,
    _HEADER_ENUMS,
)
from gd.api.hsv import HSV

__all__ = ("_template", "_create", "_object_code", "_color_code", "_header_code", "_level_code")

_template = """
@property
def {name}(self):
    \"\"\":class:`{cls}`: Property ({desc}).\"\"\"
    return self.data.get({enum!r})
@{name}.setter
def {name}(self, value):
    self.data[{enum!r}] = value
@{name}.deleter
def {name}(self):
    try:
        del self.data[{enum!r}]
    except KeyError:
        pass
""".strip()

_container = "_container = {}"


def _get_type(key: Union[int, str], type_str: str = "object") -> str:
    type_map = {
        "object": {
            key in _INT: int,
            key in _BOOL: bool,
            key in _FLOAT: float,
            key in _HSV: HSV,
            key in _ENUMS: _ENUMS.get(key),
            key == _TEXT: str,
            key == _GROUPS: set,
        },
        "color": {
            key in _COLOR_INT: int,
            key in _COLOR_BOOL: bool,
            key == _COLOR_PLAYER: PlayerColor,
            key == _COLOR_FLOAT: float,
            key == _COLOR_HSV: HSV,
        },
        "header": {
            key in _HEADER_INT: int,
            key in _HEADER_BOOL: bool,
            key == _HEADER_FLOAT: float,
            key in _HEADER_COLORS: "ColorChannel",
            key == _COLORS: list,
            key == _GUIDELINES: list,
            key in _HEADER_ENUMS: _HEADER_ENUMS.get(key),
        },
        "level": {True: "WIP"},  # yikes!
    }
    result = type_map.get(type_str, {}).get(True, str)

    try:
        return result.__name__
    except AttributeError:
        return result


def _create(enum: Enum, type_str: str) -> str:
    final = []

    for name, value in enum.as_dict().items():
        desc = enum(value).title
        value = str(value)
        cls = _get_type(value, type_str)
        final.append(_template.format(name=name, enum=value, desc=desc, cls=cls))

    property_container = {}

    for name, value in enum.as_dict().items():

        value = str(value)  # we are going with str from now on

        if value not in property_container:
            property_container[value] = name

    final.append(_container.format(property_container))

    return ("\n\n").join(final)


_object_code = _create(ObjectDataEnum, "object")
_color_code = _create(ColorChannelProperties, "color")
_header_code = _create(LevelHeaderEnum, "header")
_level_code = _create(LevelDataEnum, "level")
