# DOCUMENT

from gd.memory.data import Data
from gd.memory.traits import Layout
from gd.platform import Platform, system_bits, system_platform
from gd.text_utils import make_repr
from gd.typing import Callable, Dict, Type, TypeVar

__all__ = (
    "Types",
    "types",
    "c_byte",
    "c_ubyte",
    "c_short",
    "c_ushort",
    "c_int",
    "c_uint",
    "c_long",
    "c_ulong",
    "c_longlong",
    "c_ulonglong",
    "c_float",
    "c_double",
    "c_bool",
    "boolean",
    "float32",
    "float64",
    "int8",
    "uint8",
    "int16",
    "uint16",
    "int32",
    "uint32",
    "int64",
    "uint64",
    "intptr",
    "uintptr",
    "intsize",
    "uintsize",
    "get_c_int_type",
    "get_c_uint_type",
    "get_intptr",
    "get_uintptr",
    "get_intsize",
    "get_uintsize",
)

T = TypeVar("T")


class c_byte(Data[int], name="c_byte", format="b"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_ubyte(Data[int], name="c_ubyte", format="B"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_short(Data[int], name="c_short", format="h"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_ushort(Data[int], name="c_ushort", format="H"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_int(Data[int], name="c_int", format="i"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_uint(Data[int], name="c_uint", format="I"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_long(Data[int], name="c_long", format="l"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_ulong(Data[int], name="c_ulong", format="L"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_longlong(Data[int], name="c_longlong", format="q"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


class c_ulonglong(Data[int], name="c_ulonglong", format="Q"):
    def __init__(self, value: int = 0) -> None:
        self._value = value


c_int_types = (c_byte, c_short, c_int, c_long, c_longlong)
c_uint_types = (c_ubyte, c_ushort, c_uint, c_ulong, c_ulonglong)


def get_c_int_type(bits: int) -> Type[Data[int]]:
    for c_int_type in c_int_types:
        if c_int_type.bits == bits:
            return c_int_type

    raise LookupError(f"Can not find C signed integer type with {bits} bits.")


def get_c_uint_type(bits: int) -> Type[Data[int]]:
    for c_uint_type in c_uint_types:
        if c_uint_type.bits == bits:
            return c_uint_type

    raise LookupError(f"Can not find C unsigned integer type with {bits} bits.")


try:
    class int8(Data[int], name="int8", format=get_c_int_type(8).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class uint8(Data[int], name="uint8", format=get_c_uint_type(8).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class int16(Data[int], name="int16", format=get_c_int_type(16).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class uint16(Data[int], name="uint16", format=get_c_uint_type(16).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class int32(Data[int], name="int32", format=get_c_int_type(32).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class uint32(Data[int], name="uint32", format=get_c_uint_type(32).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class int64(Data[int], name="int64", format=get_c_int_type(64).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value

    class uint64(Data[int], name="uint64", format=get_c_uint_type(64).format):
        def __init__(self, value: int = 0) -> None:
            self._value = value


except KeyError as error:
    raise LookupError("Can not find all integer types.") from error


int_types = (int8, int16, int32, int64)
uint_types = (uint8, uint16, uint32, uint64)


def get_int_type(bits: int) -> Type[Data[int]]:
    for int_type in int_types:
        if int_type.bits == bits:
            return int_type

    raise LookupError(f"Can not find signed integer type with {bits} bits.")


def get_uint_type(bits: int) -> Type[Data[int]]:
    for uint_type in uint_types:
        if uint_type.bits == bits:
            return uint_type

    raise LookupError(f"Can not find unsigned integer type with {bits} bits.")


def get_intptr(bits: int) -> Type[Data[int]]:
    return get_int_type(bits)


def get_uintptr(bits: int) -> Type[Data[int]]:
    return get_uint_type(bits)


def get_intsize(bits: int) -> Type[Data[int]]:
    return get_int_type(bits)


def get_uintsize(bits: int) -> Type[Data[int]]:
    return get_uint_type(bits)


intptr = get_intptr(system_bits)
uintptr = get_uintptr(system_bits)

intsize = get_intsize(system_bits)
uintsize = get_uintsize(system_bits)


class c_float(Data[float], name="c_float", format="f"):
    def __init__(self, value: float = 0.0) -> None:
        self._value = value


class c_double(Data[float], name="c_double", format="d"):
    def __init__(self, value: float = 0.0) -> None:
        self._value = value


class float32(Data[float], name="float32", format=c_float.format):
    def __init__(self, value: float = 0.0) -> None:
        self._value = value


class float64(Data[float], name="float64", format=c_double.format):
    def __init__(self, value: float = 0.0) -> None:
        self._value = value


class c_bool(Data[bool], name="c_bool", format="?"):
    def __init__(self, value: bool = False) -> None:
        self._value = value


class boolean(Data[bool], name="boolean", format=c_bool.format):
    def __init__(self, value: bool = False) -> None:
        self._value = value


L = TypeVar("L", bound=Layout)

GetType = Callable[[int, Platform], Type[L]]


def get_type_wrap(type: Type[L]) -> GetType[L]:
    def get_type(bits: int, platform: Platform) -> Type[L]:
        return type

    return get_type


class Types:
    TYPES: Dict[str, GetType] = {}

    def __init__(self, bits: int = system_bits, platform: Platform = system_platform) -> None:
        self.bits = bits
        self.platform = platform

    def __repr__(self) -> str:
        info = {"bits": self.bits, "platform": self.platform.name.casefold()}

        return make_repr(self, info)

    def get(self, name: str) -> Type[L]:
        return self.fetch(name)(self.bits, self.platform)

    __getattr__ = get

    @classmethod
    def _register(cls, name: str, get_type: GetType[L]) -> GetType[L]:
        return cls.TYPES.setdefault(name, get_type)

    @classmethod
    def register(cls, name: str) -> Callable[[GetType[L]], GetType[L]]:
        def decorator(get_type: GetType[L]) -> GetType[L]:
            return cls._register(name, get_type)

        return decorator

    @classmethod
    def register_function(cls, get_type: GetType[L]) -> GetType[L]:
        return cls._register(get_type.__name__, get_type)

    @classmethod
    def register_type(cls, name: str, type: Type[L]) -> GetType[L]:
        return cls._register(name, get_type_wrap(type))

    @classmethod
    def fetch(cls, name: str) -> GetType[L]:
        if name in cls.TYPES:
            return cls.TYPES[name]

        raise LookupError(f"Can not find any types for {name!r}.")


types = Types


@types.register_function
def byte_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int8


@types.register_function
def ubyte_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint8


@types.register_function
def short_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int16


@types.register_function
def ushort_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint16


@types.register_function
def int_t(bits: int, platform: Platform) -> Type[Data[int]]:
    if bits < 32:
        return int16

    return int32


@types.register_function
def uint_t(bits: int, platform: Platform) -> Type[Data[int]]:
    if bits < 32:
        return uint16

    return uint32


@types.register_function
def long_t(bits: int, platform: Platform) -> Type[Data[int]]:
    if bits > 32:
        return int64

    return int32


@types.register_function
def ulong_t(bits: int, platform: Platform) -> Type[Data[int]]:
    if bits > 32:
        return uint64

    return uint32


@types.register_function
def longlong_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int64


@types.register_function
def ulonglong_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint64


@types.register_function
def int8_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int8


@types.register_function
def uint8_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint8


@types.register_function
def int16_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int16


@types.register_function
def uint16_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint16


@types.register_function
def int32_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int32


@types.register_function
def uint32_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint32


@types.register_function
def int64_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return int64


@types.register_function
def uint64_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint64


@types.register_function
def intptr_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return get_intptr(bits)


@types.register_function
def uintptr_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return get_uintptr(bits)


@types.register_function
def intsize_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return get_intsize(bits)


@types.register_function
def uintsize_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return get_uintsize(bits)


@types.register_function
def float_t(bits: int, platform: Platform) -> Type[Data[float]]:
    return c_float


@types.register_function
def double_t(bits: int, platform: Platform) -> Type[Data[float]]:
    return c_double


@types.register_function
def char_t(bits: int, platform: Platform) -> Type[Data[int]]:
    return uint8


@types.register_function
def float32_t(bits: int, platform: Platform) -> Type[Data[float]]:
    return float32


@types.register_function
def float64_t(bits: int, platform: Platform) -> Type[Data[float]]:
    return float64


@types.register_function
def bool_t(bits: int, platform: Platform) -> Type[Data[bool]]:
    return c_bool
