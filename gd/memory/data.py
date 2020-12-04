import ctypes
from struct import calcsize, pack, unpack

from gd.decorators import cache_by
from gd.enums import ByteOrder
from gd.text_utils import make_repr
from gd.typing import Any, Dict, Generic, Sequence, Tuple, Type, TypeVar, Union, cast

__all__ = (
    "BYTE_BITS",
    "SIZE_BITS",
    "Buffer",
    "Data",
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

_bytes_from_hex = bytes.fromhex


def _bytes_to_hex(data: bytes, step: int = 1) -> str:
    return " ".join(data[index : index + step].hex() for index in range(0, len(data), step))


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
        cls._size = calcsize(format)

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
        return cls._size * BYTE_BITS


class Data(Generic[T], metaclass=DataMeta, name="Data"):
    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{self.name}({self.value!r})"

    @classmethod
    def from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> "Data[T]":
        return cls(cls.value_from_bytes(data, order))

    def to_bytes(self, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return self.value_to_bytes(self.value, order)

    @classmethod
    def value_from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> T:
        result = unpack(cls.create_format(order), data)

        if len(result) == 1:
            (result,) = result

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
        return self.type._size * BYTE_BITS


EMPTY_BYTES = bytes(0)


class BufferMeta(type):
    def __getitem__(cls, item: Union[int, Sequence[int]]) -> "Buffer":
        if isinstance(item, Sequence):
            return cls.from_byte_array(item)

        return cls.from_byte_array([item])

    def from_byte_array(cls, array: Sequence[int]) -> "Buffer":
        raise NotImplementedError("This function is implemented in the actual class.")


class Buffer(metaclass=BufferMeta):
    def __init__(self, data: bytes = EMPTY_BYTES) -> None:
        self._data = data

    def __str__(self) -> str:
        return self.to_hex().upper()

    def __repr__(self) -> str:
        info = {"data": repr(self.to_hex().upper())}
        return make_repr(self, info)

    @property
    def data(self) -> bytes:
        return self._data

    @classmethod
    def from_value(
        cls, type: Type[Data[T]], value: T, byte_order: Union[str, ByteOrder] = ByteOrder.NATIVE
    ) -> "Buffer":
        return cls(type.value_to_bytes(value, byte_order))

    def to_value(
        self, type: Type[Data[T]], byte_order: Union[str, ByteOrder] = ByteOrder.NATIVE
    ) -> T:
        return type.value_from_bytes(self.data, byte_order)

    @classmethod
    def from_byte_array(cls, array: Sequence[int]) -> "Buffer":
        return cls(bytes(array))

    def to_byte_array(self) -> Sequence[int]:
        return list(self.data)

    @classmethod
    def from_hex(cls, hex_string: str) -> "Buffer":
        return cls(_bytes_from_hex(hex_string))

    def to_hex(self, step: int = 1) -> str:
        return _bytes_to_hex(self._data, step)

    def into_buffer(self) -> Any:
        return ctypes.create_string_buffer(self.data, len(self.data))

    def into(self) -> bytes:
        return self.data


class c_ptr(Data[int], name="c_ptr", format="P"):
    pass


SIZE_BITS = cast(int, c_ptr.bits)


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


def get_intptr(bits: int = SIZE_BITS) -> Type[Data[int]]:
    return get_c_int_type(bits)


def get_uintptr(bits: int = SIZE_BITS) -> Type[Data[int]]:
    return get_c_uint_type(bits)


def get_intsize(bits: int = SIZE_BITS) -> Type[Data[int]]:
    return get_c_int_type(bits)


def get_uintsize(bits: int = SIZE_BITS) -> Type[Data[int]]:
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


class TypeHandler:
    def __init__(self, bits: int) -> None:
        self.bits = bits

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
