from ..utils.wrap_tools import make_repr
from ..utils.enums import NEnum
from ..utils.crypto.coders import Coder

from .enums import *

__all__ = ('Object', 'HSV')


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
        n = _get_id(name)

        if n is None:
            return

        return self.data.get(n, default_value(n))

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

    @classmethod
    def from_mapping(cls, mapping: dict):
        self = cls()
        self.data = mapping
        return self

    @classmethod
    def from_string(cls, string: str):
        mapping = _convert(string.split(','))
        return cls.from_mapping(mapping)


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
            int(h), _maybefloat(s), _maybefloat(v), bool(int(s_checked)), bool(int(v_checked))
        )

        return cls(*value_tuple)

    def dump(self):
        value_tuple = (
            self.h, self.s, self.v,
            int(self.s_checked), int(self.v_checked)
        )
        return 'a'.join(map(str, value_tuple))


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

        if n == 31:  # Text
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


def define_type(n: int):
    cases = {
        n in {
            1, 7, 8, 9, 12, 20, 21, 22, 23, 24, 25, 50, 51, 61, 71, 76, 77, 80, 82, 95, 108
        }: int,
        n in {
            4, 5, 11, 13, 14, 15, 16, 17, 34, 36, 41, 42, 48, 52, 56, 58, 59, 60, 62, 64, 65,
            66, 67, 70, 78, 81, 86, 87, 89, 93, 94, 96, 98, 99, 100, 102, 103, 106
        }: bool,
        n in {
            2, 3, 6, 10, 28, 29, 30, 32, 35, 45, 46, 47, 54, 63, 68, 69, 72, 73, 75, 84, 85,
            90, 91, 92, 97, 105, 107
        }: _maybefloat,
        n == 31: lambda string: _b64_failsafe(string, encode=False),
        n == 57: _ints_from_str,
        n in {43, 44, 49}: HSV.from_string,
        n == 79: lambda n: PickupItemMode.from_value(int(n)),
        n == 88: lambda n: InstantCountComparison.from_value(int(n)),
        n == 101: lambda n: TargetPosCoordinates.from_value(int(n)),
    }
    return cases.get(True, str)


def default_value(n: int):
    if n == 57:
        return list()

    if n == 31:
        return str()

    value = 0
    if n in {43, 44, 49}:
        value = '0a0a0a0a0'

    func = define_type(n)

    return func(value)


def _iter_to_str(x):
    return ('.').join(map(str, x))


def map_type(x: type):
    mapping = {
        float: float,
        int: int,
        str: str,
        list: _iter_to_str,
        tuple: _iter_to_str,
        HSV: HSV.dump,
        NEnum: lambda enum: enum.value
    }
    c_type = str

    for type_1, type_2 in mapping.items():
        if isinstance(x, type_1):
            c_type = type_2
            break

    return c_type
