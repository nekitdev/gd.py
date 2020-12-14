from gd.decorators import cache_by
from gd.memory.data import Data, data
from gd.platform import system_bits
from gd.text_utils import make_repr
from gd.typing import Type, TypeVar

__all__ = (
    "TypeHandler",
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

BYTE_BITS = 8


@data(name="c_byte", format="b")
class c_byte(Data[int]):
    pass


@data(name="c_ubyte", format="B")
class c_ubyte(Data[int]):
    pass


@data(name="c_short", format="h")
class c_short(Data[int]):
    pass


@data(name="c_ushort", format="H")
class c_ushort(Data[int]):
    pass


@data(name="c_int", format="i")
class c_int(Data[int]):
    pass


@data(name="c_uint", format="I")
class c_uint(Data[int]):
    pass


@data(name="c_long", format="l")
class c_long(Data[int]):
    pass


@data(name="c_ulong", format="L")
class c_ulong(Data[int]):
    pass


@data(name="c_longlong", format="q")
class c_longlong(Data[int]):
    pass


@data(name="c_ulonglong", format="Q")
class c_ulonglong(Data[int]):
    pass


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
    @data(name="int8", format=get_c_int_type(8).format)
    class int8(Data[int]):
        pass

    @data(name="uint8", format=get_c_uint_type(8).format)
    class uint8(Data[int]):
        pass

    @data(name="int16", format=get_c_int_type(16).format)
    class int16(Data[int]):
        pass

    @data(name="uint16", format=get_c_uint_type(16).format)
    class uint16(Data[int]):
        pass

    @data(name="int32", format=get_c_int_type(32).format)
    class int32(Data[int]):
        pass

    @data(name="uint32", format=get_c_uint_type(32).format)
    class uint32(Data[int]):
        pass

    @data(name="int64", format=get_c_int_type(64).format)
    class int64(Data[int]):
        pass

    @data(name="uint64", format=get_c_uint_type(64).format)
    class uint64(Data[int]):
        pass


except KeyError as error:
    raise LookupError("Can not find all integer types.") from error


def get_intptr(bits: int) -> Type[Data[int]]:
    return get_c_int_type(bits)


def get_uintptr(bits: int) -> Type[Data[int]]:
    return get_c_uint_type(bits)


def get_intsize(bits: int) -> Type[Data[int]]:
    return get_c_int_type(bits)


def get_uintsize(bits: int) -> Type[Data[int]]:
    return get_c_uint_type(bits)


intptr = get_intptr(system_bits)
uintptr = get_uintptr(system_bits)

intsize = get_intsize(system_bits)
uintsize = get_uintsize(system_bits)


@data(name="c_float", format="f")
class c_float(Data[float]):
    pass


@data(name="c_double", format="d")
class c_double(Data[float]):
    pass


@data(name="float32", format=c_float.format)
class float32(Data[float]):
    pass


@data(name="float64", format=c_double.format)
class float64(Data[float]):
    pass


@data(name="c_bool", format="?")
class c_bool(Data[bool]):
    pass


@data(name="boolean", format=c_bool.format)
class boolean(Data[bool]):
    pass


class TypeHandler:
    def __init__(self, bits: int) -> None:
        self.bits = bits

    def __repr__(self) -> str:
        info = {"bits": self.bits}

        return make_repr(self, info)

    @property
    def byte_t(self) -> Type[Data[int]]:
        return int8

    @property
    def ubyte_t(self) -> Type[Data[int]]:
        return uint8

    @property
    def short_t(self) -> Type[Data[int]]:
        return int16

    @property
    def ushort_t(self) -> Type[Data[int]]:
        return uint16

    @property
    def int_t(self) -> Type[Data[int]]:
        if self.bits < 32:
            return int16

        return int32

    @property
    def uint_t(self) -> Type[Data[int]]:
        if self.bits < 32:
            return uint16

        return uint32

    @property
    def long_t(self) -> Type[Data[int]]:
        if self.bits > 32:
            return int64

        return int32

    @property
    def ulong_t(self) -> Type[Data[int]]:
        if self.bits > 32:
            return uint64

        return uint32

    @property
    def longlong_t(self) -> Type[Data[int]]:
        return int64

    @property
    def ulonglong_t(self) -> Type[Data[int]]:
        return uint64

    @property
    def int8_t(self) -> Type[Data[int]]:
        return int8

    @property
    def uint8_t(self) -> Type[Data[int]]:
        return uint8

    @property
    def int16_t(self) -> Type[Data[int]]:
        return int16

    @property
    def uint16_t(self) -> Type[Data[int]]:
        return uint16

    @property
    def int32_t(self) -> Type[Data[int]]:
        return int32

    @property
    def uint32_t(self) -> Type[Data[int]]:
        return uint32

    @property
    def int64_t(self) -> Type[Data[int]]:
        return int64

    @property
    def uint64_t(self) -> Type[Data[int]]:
        return uint64

    @property  # type: ignore
    @cache_by("bits")
    def intptr_t(self) -> Type[Data[int]]:
        return get_intptr(self.bits)

    @property  # type: ignore
    @cache_by("bits")
    def uintptr_t(self) -> Type[Data[int]]:
        return get_uintptr(self.bits)

    @property  # type: ignore
    @cache_by("bits")
    def intsize_t(self) -> Type[Data[int]]:
        return get_intsize(self.bits)

    @property  # type: ignore
    @cache_by("bits")
    def uintsize_t(self) -> Type[Data[int]]:
        return get_uintsize(self.bits)

    @property
    def float_t(self) -> Type[Data[float]]:
        return c_float

    @property
    def double_t(self) -> Type[Data[float]]:
        return c_double

    @property
    def float32_t(self) -> Type[Data[float]]:
        return float32

    @property
    def float64_t(self) -> Type[Data[float]]:
        return float64

    @property
    def bool_t(self) -> Type[Data[bool]]:
        return c_bool
