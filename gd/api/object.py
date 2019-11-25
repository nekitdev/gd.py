from ..utils.wrap_tools import make_repr
from ..utils.enums import NEnum
from ..utils.crypto.coders import Coder

from ..errors import EditorError

from .hsv import HSV

from .enums import *

__all__ = ('Object',)


class Object:
    def __init__(self, **properties):
        self.data = {}

        for name, value in properties.items():
            n = _get_id(name)
            if n:
                self.data[n] = value

    def __repr__(self):
        info = {key: repr(value) for key, value in self.to_dict().items()}
        return make_repr(self, info)

    def __getattr__(self, name):
        try:
            return self.data[_get_id(name)]
        except KeyError:
            raise AttributeError(
                '{0.__class__.__name__!r} object '
                'has no attribute {1!r}.'.format(self, name)
            ) from None

    def __setattr__(self, name, value):
        n = _get_id(name)

        if n:
            self.data[n] = value

        else:
            self.__dict__[name] = value

    def to_dict(self):
        return _load(self.data)

    def dump(self):
        return _collect(self.to_map())

    def to_map(self):
        data = {1: 1, 2: 0, 3: 0}
        data.update(self.data)
        return _dump(data)

    def copy(self):
        self_copy = self.__class__()
        self_copy.data = self.data.copy()
        return self_copy

    def edit(self, **fields):
        for field, value in fields.items():
            setattr(self, field, value)

    @classmethod
    def from_mapping(cls, mapping: dict):
        self = cls()
        self.data = mapping
        return self

    @classmethod
    def from_string(cls, string: str):
        try:
            mapping = _convert(string.split(','))
            return cls.from_mapping(mapping)

        except Exception as exc:
            raise EditorError('Failed to process object string.') from exc


def _get_name(n):
    try:
        name = ObjectDataEnum.from_value(n).name.lower()
    except Exception:
        name = 'unknown_' + str(n).replace('-', '_')

    return name


def _load(d):
    return {_get_name(n): value for n, value in d.items()}


def _try_convert(obj, cls: type = int):
    try:
        return cls(obj)
    except Exception:
        return obj


def _convert(s):
    final = {}

    zip_map = zip(s[::2], s[1::2])

    for key, value in zip_map:
        n = _try_convert(key)
        final[n] = define_type(n)(value)

    return final


def _get_id(name: str):
    try:
        n = ObjectDataEnum.from_value(name).value

    except Exception:
        name = str(name).lstrip('unknown')

        if name.startswith('_'):
            name = name[1:]

        name = name.replace('_', '-')

        try:
            n = int(name)

        except ValueError:
            return 0

    return n


def _dump(d):
    final = {}

    for n, value in d.items():
        to_add = map_type(value)(value)

        if n == _TEXT:
            to_add = _b64_failsafe(to_add, encode=True)

        final[n] = to_add

    return final


def _collect(d, char: str = ','):
    def generator():
        for key, value in d.items():
            yield from map(str, (key, value))

    return char.join(generator())


def _maybefloat(s: str):
    if '.' in s:
        return float(s)
    return int(s)


def _ints_from_str(string: str, split: str = '.'):
    string = str(string)  # just in case
    return list(map(int, string.split(split)))


def _b64_failsafe(string: str, encode: bool = True):
    try:
        return Coder.do_base64(string, encode=encode)
    except Exception:
        return string


_INT = {
    1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71, 
    76, 77, 80, 95, 108
}

_BOOL = {
    4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 56, 58, 59, 60, 62, 64, 65,
    66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
}

_FLOAT = {
    2, 3, 6, 10, 28, 29, 30, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75,
    84, 85, 90, 91, 92, 97, 105, 107
}

_HSV = {43, 44, 49}

_TEXT = 31
_GROUPS = 57

_PULSE_MODE = 48
_PULSE_TYPE = 52
_PICKUP_MODE = 79
_TOUCH_TOGGLE = 82
_COMP = 88
_TARGET_COORDS = 101

_ENUMS = {
    _PULSE_MODE: lambda n: PulseMode(int(n)),
    _PULSE_TYPE: lambda n: PulseType(int(n)),
    _PICKUP_MODE: lambda n: PickupItemMode(int(n)),
    _TOUCH_TOGGLE: lambda n: TouchToggleMode(int(n)),
    _COMP: lambda n: InstantCountComparison(int(n)),
    _TARGET_COORDS: lambda n: TargetPosCoordinates(int(n))
}


def _bool(s: str):
    return s == '1'


def define_type(n: int):
    cases = {
        n in _INT: int,
        n in _BOOL: _bool,
        n in _FLOAT: _maybefloat,
        n == _TEXT: lambda string: _b64_failsafe(string, encode=False),
        n == _GROUPS: _ints_from_str,
        n in _HSV: HSV.from_string,
        n in _ENUMS: _ENUMS.get(n)
    }
    return cases.get(True, str)


def _iter_to_str(x):
    return ('.').join(map(str, x))


_MAPPING = {
    float: float,
    int: int,
    str: str,
    list: _iter_to_str,
    tuple: _iter_to_str,
    HSV: HSV.dump,
    NEnum: lambda enum: enum.value
}


def map_type(x: type):
    c_type = str
    for type_1, type_2 in _MAPPING.items():
        if isinstance(x, type_1):
            c_type = type_2
            break

    return c_type