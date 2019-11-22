from ..utils.mapper import mapper
from ..utils.wrap_tools import make_repr
from ..utils.enums import NEnum
from ..utils.crypto.coders import Coder

from .enums import *

__all__ = ('Object', 'HSV')


class Object:
    def __init__(self, **properties):
        self.data = properties

    def __repr__(self):
        info = {key: repr(value) for key, value in self.data.items()}
        return make_repr(self, info)

    def __setattr__(self, name, attr):
        if name != 'data':
            self.data[name] = attr
        else:
            self.__dict__[name] = attr

        self.__dict__.update(self.data)

    def __getattr__(self, name):
        n = _get_id(name)

        if n is None:
            return n

        return default_value(n)

    def to_int_map(self):
        data = {'id': 1, 'x': 0, 'y': 0}
        data.update(self.data)

        return _dump(data)

    def dump(self):
        return _collect(self.to_int_map())

    @classmethod
    def from_mapping(cls, mapping: dict):
        mapping = _convert(mapping)
        return cls(**mapping)

    @classmethod
    def from_string(cls, string: str):
        properties = mapper.map(string.split(','))
        return cls.from_mapping(properties)


def _convert(d):
    final = {}

    for n, value in d.items():
        try:
            name = ObjectDataEnum.from_value(n).name.lower()
        except Exception:
            name = 'unknown_' + str(n).replace('-', '_')

        final[name] = define_type(n)(value)

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
            return

    return n


def _dump(d):
    final = {}

    for name, value in d.items():
        n = _get_id(name)

        if n is not None:
            to_add = map_type(value)(value)

            if n == 31:  # Text
                to_add = _b64_failsafe(str(to_add), encode=True)

            final[n] = to_add

    return final


def _collect(d, char: str = ','):
    def generator():
        for key, value in d.items():
            yield from map(str, (key, value))

    return char.join(generator())


class HSV:
    def __init__(
        self, h: int = 0, s: float = 0, v: float = 0,
        s_checked: bool = False, v_checked: bool = False
    ):
        self.h = h
        self.s = s
        self.v = v
        self.s_checked = s_checked
        self.v_checked = v_checked

    def __repr__(self):
        info = {
            'h': self.h,
            's': self.s,
            'v': self.v,
            's_checked': self.s_checked,
            'v_checked': self.v_checked
        }
        return make_repr(self, info)

    @classmethod
    def from_string(cls, string: str):
        h, s, v, s_checked, v_checked = string.split('a')

        value_tuple = (
            int(h), float(s), float(v), bool(int(s_checked)), bool(int(v_checked))
        )

        return cls(*value_tuple)

    def dump(self):
        value_tuple = (
            int(self.h), _maybefloat(self.s), _maybefloat(self.v),
            int(self.s_checked), int(self.v_checked)
        )
        return 'a'.join(map(str, value_tuple))


def _maybefloat(n: float):
    return int(n) if n.is_integer() else n


def _ints_from_str(string: str, split: str = '.'):
    return list(map(int, string.split(split)))


def _b64_failsafe(string: str, encode: bool = True):
    try:
        return gd.Coder.do_base64(string, encode=encode)
    except Exception:
        return string


def define_type(n: int):
    cases = {
        n in (
            1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71, 76, 77, 80, 82, 95, 108
        ): int,
        n in (
            4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 48, 52, 56, 58, 59, 60, 62, 64, 65,
            66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
        ): bool,
        n in (
            2, 3, 6, 10, 28, 29, 30, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75, 84, 85,
            90, 91, 92, 97, 105, 107
        ): float,
        n == 31: lambda string: _b64_failsafe(string, encode=False)
        n == 57: _ints_from_str,
        n in (43, 44, 49): HSV.from_string,
        n == 79: PickupItemMode.from_value,
        n == 88: InstantCountComparison.from_value,
        n == 101: TargetPosCoordinates.from_value
    }
    return cases.get(True, str)


def default_value(n: int):
    if n == 57:
        return list()

    if n == 31:
        return str()

    value = 0
    if n in (43, 44, 49):
        value = '0a0a0a0a0'

    func = define_type(n)

    return func(value)


def map_type(x: type):
    mapping = {
        float: _maybefloat,
        int: int,
        str: str,
        list: lambda x: ('.').join(map(str, x)),
        NEnum: lambda enum: enum.value
    }
    c_type = str

    for type_1, type_2 in mapping.items():
        if isinstance(x, type_1):
            c_type = type_2
            break

    return c_type
