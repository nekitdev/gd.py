"""Automatic object property code generator."""

from gd.typing import Enum, Union

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


def _get_type(n: Union[int, str], ts: str = "object") -> str:
    t = {
        "object": {
            n in _INT: int,
            n in _BOOL: bool,
            n in _FLOAT: float,
            n in _HSV: HSV,
            n in _ENUMS: _ENUMS.get(n),
            n == _TEXT: str,
            n == _GROUPS: set,
        },
        "color": {
            n in _COLOR_INT: int,
            n in _COLOR_BOOL: bool,
            n == _COLOR_PLAYER: PlayerColor,
            n == _COLOR_FLOAT: float,
            n == _COLOR_HSV: HSV,
        },
        "header": {
            n in _HEADER_INT: int,
            n in _HEADER_BOOL: bool,
            n == _HEADER_FLOAT: float,
            n in _HEADER_COLORS: "ColorChannel",
            n == _COLORS: list,
            n == _GUIDELINES: list,
            n in _HEADER_ENUMS: _HEADER_ENUMS.get(n),
        },
        "level": {True: "soon"},  # yikes!
    }
    r = t.get(ts, {}).get(1, str)

    try:
        return r.__name__
    except AttributeError:
        return r


def _create(enum: Enum, ts: str) -> str:
    final = []

    for name, value in enum.as_dict().items():
        desc = enum(value).desc
        value = str(value)
        cls = _get_type(value, ts=ts)
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
