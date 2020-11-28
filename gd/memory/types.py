import ctypes
from struct import calcsize as calculate_size, pack, unpack

from gd.enums import ByteOrder
from gd.typing import Any, Dict, Generic, Tuple, Type, TypeVar, Union, cast

__all__ = (
    "Data",
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

_byte_bits = 8

_bitness = ctypes.sizeof(ctypes.c_void_p) * _byte_bits


class DataMeta(type):
    _name: str = ""
    _format: str = ""
    _size: int = 0

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        name: str,
        format: str = "",
    ) -> "DataMeta":
        cls = cast(DataMeta, super().__new__(meta_cls, cls_name, bases, cls_dict))

        cls._name = name

        cls._format = format
        cls._size = calculate_size(format)

        return cls

    def __repr__(cls) -> str:
        return cls.name

    def create_format(cls, order: Union[str, ByteOrder]) -> str:
        return ByteOrder.from_value(order).value + cls.format

    @property
    def name(cls) -> str:
        return cls._name

    @property
    def format(cls) -> str:
        return cls._format

    @property
    def size(cls) -> int:
        return cls._size

    @property
    def bits(cls) -> int:
        return cls._size * _byte_bits


class Data(Generic[T], metaclass=DataMeta, name="Data"):
    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{self.name}({self.value!r})"

    @classmethod
    def from_bytes(
        cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE
    ) -> "Data[T]":
        return cls(cls.value_from_bytes(data, order))

    def to_bytes(self, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return self.value_to_bytes(self.value, order)

    @classmethod
    def value_from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> T:
        result = unpack(cls.create_format(order), data)

        if len(result) == 1:
            result, = result

        return cast(T, result)

    @classmethod
    def value_to_bytes(cls, value: T, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return pack(cls.create_format(order), value)

    @property
    def value(self) -> T:
        return self._value

    @property
    def type(self) -> Type["Data[T]"]:
        return self.__class__

    @property
    def name(self) -> str:
        return self.type._name

    @property
    def format(self) -> str:
        return self.type._format

    @property
    def size(self) -> int:
        return self.type._size

    @property
    def bits(self) -> int:
        return self.type._size * _byte_bits


class c_byte(Data[int], name="c_byte", format="b"):
    pass


class c_ubyte(Data[int], name="c_ubyte", format="B"):
    pass


class c_short(Data[int], name="c_short", format="h"):
    pass


class c_ushort(Data[int], name="c_ushort", format="H"):
    pass


class c_int(Data[int], name="c_int", format="i"):
    pass


class c_uint(Data[int], name="c_uint", format="I"):
    pass


class c_long(Data[int], name="c_long", format="l"):
    pass


class c_ulong(Data[int], name="c_ulong", format="L"):
    pass


class c_longlong(Data[int], name="c_longlong", format="q"):
    pass


class c_ulonglong(Data[int], name="c_ulonglong", format="Q"):
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
    class int8(Data[int], name="int8", format=get_c_int_type(8).format):
        pass

    class uint8(Data[int], name="uint8", format=get_c_uint_type(8).format):
        pass

    class int16(Data[int], name="int16", format=get_c_int_type(16).format):
        pass

    class uint16(Data[int], name="uint16", format=get_c_uint_type(16).format):
        pass

    class int32(Data[int], name="int32", format=get_c_int_type(32).format):
        pass

    class uint32(Data[int], name="uint32", format=get_c_uint_type(32).format):
        pass

    class int64(Data[int], name="int64", format=get_c_int_type(64).format):
        pass

    class uint64(Data[int], name="uint64", format=get_c_uint_type(64).format):
        pass

except KeyError as error:
    raise LookupError("Can not find all integer types.") from error


def get_intptr(bits: int = _bitness) -> Type[Data[int]]:
    return get_c_int_type(bits)


def get_uintptr(bits: int = _bitness) -> Type[Data[int]]:
    return get_c_uint_type(bits)


def get_intsize(bits: int = _bitness) -> Type[Data[int]]:
    return get_c_int_type(bits)


def get_uintsize(bits: int = _bitness) -> Type[Data[int]]:
    return get_c_uint_type(bits)


intptr = get_intptr()
uintptr = get_uintptr()

intsize = get_intsize()
uintsize = get_uintsize()


class c_float(Data[float], name="c_float", format="f"):
    pass


class c_double(Data[float], name="c_double", format="d"):
    pass


class float32(Data[float], name="float32", format=c_float.format):
    pass


class float64(Data[float], name="float64", format=c_double.format):
    pass


class c_bool(Data[bool], name="c_bool", format="?"):
    pass


class boolean(Data[bool], name="boolean", format=c_bool.format):
    pass
