from typing import ClassVar, Type, TypeVar

from attrs import define, field

from gd.enums import Platform
from gd.memory.data import AnyData, Data
from gd.memory.traits import Layout
from gd.platform import SYSTEM_BITS, PlatformConfig
from gd.string_utils import tick
from gd.typing import DecoratorIdentity, StringDict, Unary, get_name

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
)

T = TypeVar("T")

BYTE = "b"
UBYTE = "B"
SHORT = "h"
USHORT = "H"
INT = "i"
UINT = "I"
LONG = "l"
ULONG = "L"
LONGLONG = "q"
ULONGLONG = "Q"


class c_byte(Data[int], format=BYTE):
    pass


class c_ubyte(Data[int], format=UBYTE):
    pass


class c_short(Data[int], format=SHORT):
    pass


class c_ushort(Data[int], format=USHORT):
    pass


class c_int(Data[int], format=INT):
    pass


class c_uint(Data[int], format=UINT):
    pass


class c_long(Data[int], format=LONG):
    pass


class c_ulong(Data[int], format=ULONG):
    pass


class c_longlong(Data[int], format=LONGLONG):
    pass


class c_ulonglong(Data[int], format=ULONGLONG):
    pass


c_int_types = {
    c_byte.bits: c_byte,
    c_short.bits: c_short,
    c_int.bits: c_int,
    c_long.bits: c_long,
    c_longlong.bits: c_longlong,
}

c_uint_types = {
    c_ubyte.bits: c_ubyte,
    c_ushort.bits: c_ushort,
    c_uint.bits: c_uint,
    c_ulong.bits: c_ulong,
    c_ulonglong.bits: c_ulonglong,
}

CAN_NOT_FIND_ALL_INTEGER_TYPES = "can not find all integer types"


try:

    class int8(Data[int], format=c_int_types[8].format):
        pass

    class uint8(Data[int], format=c_uint_types[8].format):
        pass

    class int16(Data[int], format=c_int_types[16].format):
        pass

    class uint16(Data[int], format=c_uint_types[16].format):
        pass

    class int32(Data[int], format=c_int_types[32].format):
        pass

    class uint32(Data[int], format=c_uint_types[32].format):
        pass

    class int64(Data[int], format=c_int_types[64].format):
        pass

    class uint64(Data[int], format=c_uint_types[64].format):
        pass

except KeyError as error:
    raise LookupError(CAN_NOT_FIND_ALL_INTEGER_TYPES) from error


int_types = {int8.bits: int8, int16.bits: int16, int32.bits: int32, int64.bits: int64}
uint_types = {uint8.bits: uint8, uint16.bits: uint16, uint32.bits: uint32, uint64.bits: uint64}


intptr = int_types[SYSTEM_BITS]
uintptr = uint_types[SYSTEM_BITS]

intsize = int_types[SYSTEM_BITS]
uintsize = uint_types[SYSTEM_BITS]


FLOAT = "f"
DOUBLE = "d"


class c_float(Data[float], format=FLOAT):
    pass


class c_double(Data[float], name=DOUBLE):
    pass


class float32(Data[float], format=c_float.format):
    pass


class float64(Data[float], format=c_double.format):
    pass


BOOL = "?"


class c_bool(Data[bool], format=BOOL):
    pass


class boolean(Data[bool], format=c_bool.format):
    pass


L = TypeVar("L", bound=Layout)

GetType = Unary[PlatformConfig, Type[AnyData]]


def get_type_wrap(type: Type[AnyData]) -> GetType:
    def get_type(config: PlatformConfig) -> Type[AnyData]:
        return type

    return get_type


GT = TypeVar("GT", bound=GetType)

CAN_NOT_FIND_ANY_TYPES = "can not find any types for name {}"


@define()
class Types:
    TYPES: ClassVar[StringDict[GetType]] = {}

    config: PlatformConfig = field(factory=PlatformConfig.system)

    def get(self, name: str) -> Type[AnyData]:
        return self.fetch(name)(self.config)

    __getattr__ = get

    @classmethod
    def register_get_type(cls, name: str, get_type: GT) -> GT:
        return cls.TYPES.setdefault(name, get_type)

    @classmethod
    def register(cls, name: str) -> DecoratorIdentity[GT]:
        def decorator(get_type: GT) -> GT:
            return cls.register_get_type(name, get_type)

        return decorator

    @classmethod
    def register_function(cls, get_type: GT) -> GT:
        return cls.register_get_type(get_name(get_type), get_type)  # type: ignore

    @classmethod
    def register_type(cls, name: str, type: Type[AnyData]) -> GetType:
        return cls.register_get_type(name, get_type_wrap(type))

    @classmethod
    def fetch(cls, name: str) -> GetType:
        types = cls.TYPES

        if name in types:
            return types[name]

        raise LookupError(CAN_NOT_FIND_ANY_TYPES.format(tick(name)))


types = Types


@types.register_function
def byte_t(config: PlatformConfig) -> Type[Data[int]]:
    return int8


@types.register_function
def ubyte_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint8


@types.register_function
def short_t(config: PlatformConfig) -> Type[Data[int]]:
    return int16


@types.register_function
def ushort_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint16


@types.register_function
def int_t(config: PlatformConfig) -> Type[Data[int]]:
    if config.bits < 32:
        return int16

    return int32


@types.register_function
def uint_t(config: PlatformConfig) -> Type[Data[int]]:
    if config.bits < 32:
        return uint16

    return uint32


@types.register_function
def long_t(config: PlatformConfig) -> Type[Data[int]]:
    if config.bits > 32 and config.platform is not Platform.WINDOWS:
        return int64

    return int32


@types.register_function
def ulong_t(config: PlatformConfig) -> Type[Data[int]]:
    if config.bits > 32 and config.platform is not Platform.WINDOWS:
        return uint64

    return uint32


@types.register_function
def longlong_t(config: PlatformConfig) -> Type[Data[int]]:
    return int64


@types.register_function
def ulonglong_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint64


@types.register_function
def int8_t(config: PlatformConfig) -> Type[Data[int]]:
    return int8


@types.register_function
def uint8_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint8


@types.register_function
def int16_t(config: PlatformConfig) -> Type[Data[int]]:
    return int16


@types.register_function
def uint16_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint16


@types.register_function
def int32_t(config: PlatformConfig) -> Type[Data[int]]:
    return int32


@types.register_function
def uint32_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint32


@types.register_function
def int64_t(config: PlatformConfig) -> Type[Data[int]]:
    return int64


@types.register_function
def uint64_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint64


@types.register_function
def intptr_t(config: PlatformConfig) -> Type[Data[int]]:
    return int_types[config.bits]


@types.register_function
def uintptr_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint_types[config.bits]


@types.register_function
def intsize_t(config: PlatformConfig) -> Type[Data[int]]:
    return int_types[config.bits]


@types.register_function
def uintsize_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint_types[config.bits]


@types.register_function
def float_t(config: PlatformConfig) -> Type[Data[float]]:
    return float32


@types.register_function
def double_t(config: PlatformConfig) -> Type[Data[float]]:
    return float64


@types.register_function
def char_t(config: PlatformConfig) -> Type[Data[int]]:
    return uint8


@types.register_function
def float32_t(config: PlatformConfig) -> Type[Data[float]]:
    return float32


@types.register_function
def float64_t(config: PlatformConfig) -> Type[Data[float]]:
    return float64


@types.register_function
def bool_t(config: PlatformConfig) -> Type[Data[bool]]:
    return boolean
