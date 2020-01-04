# type: ignore
# we are going very polymorphic here
from itertools import chain

from ..utils.crypto.coders import Coder
from ..utils.enums import NEnum

from .hsv import HSV
from .enums import (
    ZLayer,
    Easing,
    PulseMode,
    PulseType,
    PickupItemMode,
    TouchToggleMode,
    InstantCountComparison,
    TargetPosCoordinates,
    PlayerColor,
    Gamemode,
    Speed,
)


# MAIN HELPERS

def _try_convert(obj, cls: type = int):
    try:
        return cls(obj)
    except Exception:
        return obj


def _prepare(s, delim: str):
    s = s.split(delim)
    return zip(s[::2], s[1::2])


def _convert(s, delim: str = '_', attempt_conversion: bool = True, *, f=None):
    prepared = _prepare(s, delim)

    if f is None:
        # case: no convert func
        if attempt_conversion:
            return {_try_convert(key): value for key, value in prepared}

        return dict(prepared)

    if not attempt_conversion:
        # leave the keys untouched
        return {key: f(key, value) for key, value in prepared}

    final = {}

    for key, value in prepared:
        key = _try_convert(key)
        final[key] = f(key, value)

    return final


def _dump(d, additional: dict = None):
    final = {}

    for n, value in d.items():
        to_add = _convert_type(value)

        if additional and n in additional:
            to_add = additional[n](to_add)

        final[n] = to_add

    return final


def _collect(d, char: str = '_'):
    return char.join(map(str, chain.from_iterable(d.items())))


def _maybefloat(s: str):
    if '.' in s:
        return float(s)
    return int(s)


def _bool(s: str):
    return s == '1'


def _ints_from_str(string: str, split: str = '.'):
    if not string:
        return set()

    return set(map(int, string.split(split)))


def _iter_to_str(x):
    char = '.'

    try:
        elem = next(iter(x))
    except StopIteration:
        pass

    else:
        t = type(elem)
        if t is float:
            char = '~0~'

        elif t is dict:
            char = '|'
            x = (_collect(_dump(elem)) for elem in x)

    return char.join(map(str, x))


def _b64_failsafe(string: str, encode: bool = True):
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string


# OBJECT PARSING

_INT = {
    1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71,
    76, 77, 80, 95, 108
}

_BOOL = {
    4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 56, 58, 59, 60, 62, 64, 65,
    66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
}

_FLOAT = {
    2, 3, 6, 10, 28, 29, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75,
    84, 85, 90, 91, 92, 97, 105, 107
}

_HSV = {43, 44, 49}

_TEXT = 31
_GROUPS = 57

_Z_LAYER = 24
_EASING = 30
_PULSE_MODE = 48
_PULSE_TYPE = 52
_PICKUP_MODE = 79
_TOUCH_TOGGLE = 82
_COMP = 88
_TARGET_COORDS = 101

_ENUMS = {
    _Z_LAYER: ZLayer,
    _EASING: Easing,
    _PULSE_MODE: PulseMode,
    _PULSE_TYPE: PulseType,
    _PICKUP_MODE: PickupItemMode,
    _TOUCH_TOGGLE: TouchToggleMode,
    _COMP: InstantCountComparison,
    _TARGET_COORDS: TargetPosCoordinates
}

_OBJECT_ADDITIONAL = {
    _TEXT: lambda x: _b64_failsafe(x, encode=True)
}


def _object_convert(s):
    return _convert(s, delim=(','), attempt_conversion=True, f=_from_str)


def _object_dump(d):
    return _dump(d, _OBJECT_ADDITIONAL)


def _object_collect(d):
    return _collect(d, ',')


def _from_str(n: int, v: str):
    if n in _INT:
        return int(v)
    if n in _BOOL:
        return _bool(v)
    if n in _FLOAT:
        return _maybefloat(v)
    if n == _GROUPS:
        return _ints_from_str(v)
    if n in _HSV:
        return HSV.from_string(v)
    if n in _ENUMS:
        return _ENUMS[n](int(v))
    if n == _TEXT:
        return _b64_failsafe(v, encode=False)
    return v


_MAPPING = {
    bool: int,
    list: _iter_to_str,
    tuple: _iter_to_str,
    set: _iter_to_str,
    dict: _iter_to_str,
    HSV: HSV.dump
}

_KEYS = set(_MAPPING)


def _convert_type(x: object):
    t = x.__class__
    if t in _KEYS:
        return _MAPPING[t](x)
    elif NEnum in t.__mro__:
        return x.value
    return x


# COLOR PARSING

_COLOR_INT = {1, 2, 3, 6, 9, 11, 12, 13}
_COLOR_BOOL = {5, 8, 15, 17, 18}
_COLOR_PLAYER = 4
_COLOR_FLOAT = 7
_COLOR_HSV = 10


def _parse_color(n: int, v: str):
    if n in _COLOR_INT:
        return int(v)
    if n in _COLOR_BOOL:
        return _bool(v)
    if n == _COLOR_FLOAT:
        return _maybefloat(v)
    if n == _COLOR_HSV:
        return HSV.from_string(v)
    if n == _COLOR_PLAYER:
        return PlayerColor(int(v))
    return v


def _color_convert(s):
    return _convert(s, delim=('_'), attempt_conversion=True, f=_parse_color)


def _color_dump(d):
    return _dump(d)


def _color_collect(d):
    return _collect(d, '_')


# HEADER PARSING

_HEADER_INT = {
    'kA1',
    'kA6', 'kA7', 'kA18',  # TODO: add related enums
    'kS1', 'kS2', 'kS3', 'kS4', 'kS5', 'kS6', 'kS7', 'kS8', 'kS9', 'kS10',
    'kS11', 'kS12', 'kS13', 'kS14', 'kS15', 'kS16', 'kS17', 'kS18', 'kS19', 'kS20',
    'kS39',
}
_HEADER_BOOL = {
    'kA3', 'kA5', 'kA8', 'kA9', 'kA10', 'kA11', 'kA15', 'kA16', 'kA17'
}
_HEADER_FLOAT = 'kA13'
_HEADER_COLORS = {
    'kS29', 'kS30', 'kS31', 'kS32', 'kS33', 'kS34', 'kS35', 'kS36', 'kS37'
}

_COLORS = 'kS38'
_GUIDELINES = 'kA14'

_GAMEMODE = 'kA2'
_SPEED = 'kA4'

_HEADER_ENUMS = {
    _GAMEMODE: Gamemode,
    _SPEED: Speed,
}


def _parse_header(n: str, v: str):
    if n in _HEADER_INT:
        return int(v)
    if n in _HEADER_BOOL:
        return _bool(v)
    if n in _HEADER_ENUMS:
        return _HEADER_ENUMS[n](int(v))
    if n == _COLORS:
        return _parse_colors(v)
    if n == _HEADER_FLOAT:
        return _maybefloat(v)
    if n in _HEADER_COLORS:
        from .struct import ColorChannel  # HACK: circular imports
        return ColorChannel.from_mapping(_color_convert(v))
    if n == _GUIDELINES:
        return _parse_guidelines(v)
    return v


def _parse_colors(s: str, delim: str = '|'):
    return list(filter(lambda s: s, map(_color_convert, s.split(delim))))


def _parse_guidelines(s, delim: str = '~0~'):  # wow cool splitter
    return list() if not s else list(map(float, filter(lambda s: s, s.split(delim))))


def _header_convert(s):
    return _convert(s, delim=(','), attempt_conversion=False, f=_parse_header)


def _header_dump(d):
    return _dump(d)


def _header_collect(d):
    return _collect(d, ',')


# LEVEL API

_DESC = 'k3'
_SPECIAL = 'k67'
_CRYPTED = {'k4', 'k34'}
_TAB = 'kI6'


def _parse_into_array(s: str, delim: str = '_'):
    return list(map(int, s.split(delim)))


def _join_into_string(array: list, delim: str = '_'):
    return delim.join(map(str, array))


def _attempt_zip(s: str):
    unzip = all(char not in s for char in '|;,.')
    try:
        if unzip:
            return Coder.unzip(s)
        return Coder.zip(s)
    except Exception:
        return s


def _level_dump(d: dict):
    return {k: _dump_entry(k, value) for k, value in d.items()}


def _dump_entry(n: str, v):
    if n == _SPECIAL:
        return _join_into_string(v)
    if n in _CRYPTED:
        return _attempt_zip(v)
    if n == _DESC:
        return _b64_failsafe(v, encode=True)
    if n == _TAB:
        return {str(k): str(i) for k, i in v.items()}
    return v


def _process_entry(n: str, v):
    if n == _SPECIAL:
        return _parse_into_array(v)
    if n in _CRYPTED:
        return _attempt_zip(v)
    if n == _DESC:
        return _b64_failsafe(v, encode=False)
    if n == _TAB:
        return {int(k): int(i) for k, i in v.items()}
    return v


def _process_level(d: dict):
    return {k: _process_entry(k, value) for k, value in d.items()}


# LOAD ACCELERATOR

try:
    import _gd
    locals().update(_gd.__dict__)  # hacky insertion yay
except ImportError:
    pass  # can not import? kden

__all__ = tuple(key for key in locals().keys() if key.startswith('_') and '__' not in key)
