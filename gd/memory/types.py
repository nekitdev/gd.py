# type: ignore

import ctypes
import struct

from gd.enums import Enum
from gd.text_utils import make_repr
from gd.typing import (
    Any, Dict, Generic, Optional, Tuple, Type, TypeVar, Union, cast, get_type_hints
)

ANNOTATIONS = "__annotations__"

BYTE_BITS = 8

EMPTY_BYTES = bytes(0)
NULL_BYTE = bytes(1)

# sizeof(void*) is one of the easiest ways to get our bitness
SIZE = ctypes.sizeof(ctypes.c_void_p)
SIZE_BITS = SIZE * BYTE_BITS

T = TypeVar("T")

concat = "".join


class ByteOrder(Enum):
    NATIVE = "="
    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"


def create_format(format: str, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> str:
    return ByteOrder.from_value(order).value + format


class DataMeta(type):
    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        format: str = "",
        name: Optional[str] = None,
    ) -> "DataMeta":
        if name is None:
            name = cls_name

        cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        cls.name = name

        cls.format = format

        cls.size = struct.calcsize(format)
        cls.bytes = cls.size
        cls.bits = cls.bytes * BYTE_BITS

        return cls

    def __str__(cls) -> str:
        return cls.name

    def __repr__(cls) -> str:
        info = {"name": repr(cls.name), "size": cls.size}

        return make_repr(cls, info, name=f"data {cls.__name__}")


class Data(Generic[T], metaclass=DataMeta):
    def __init__(self, value: T) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    @classmethod
    def from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> "Data[T]":
        try:
            unpacked = struct.unpack(create_format(cls.format, order), data)

        except struct.error as error:
            raise ValueError(f"Can not convert data to {cls.name}. Error: {error}.")

        return cls(cast(T, unpacked))

    def to_bytes(self, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        try:
            return struct.pack(create_format(self.format, order), self.value)

        except struct.error as error:
            raise ValueError(f"Can not convert {self.name} to data. Error: {error}.")


class SimpleDataMeta(DataMeta):
    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        format: str = "",
        name: Optional[str] = None,
    ) -> "SimpleDataMeta":
        if len(format) > 1:
            raise ValueError(
                f"Simple data expected format to be of length 0 or 1, got {len(format)}."
            )

        return super().__new__(meta_cls, cls_name, bases, cls_dict, format, name)


class SimpleData(Data[T], metaclass=SimpleDataMeta):
    @classmethod
    def from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> "SimpleData[T]":
        try:
            unpacked = struct.unpack(create_format(cls.format, order), data)

        except struct.error as error:
            raise ValueError(f"Can not convert data to {cls.name}. Error: {error}.")

        return cls(cast(T, unpacked[0]))

    def to_bytes(self, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        try:
            return struct.pack(create_format(self.format, order), self.value)

        except struct.error as error:
            raise ValueError(f"Can not convert {self.name} to data. Error: {error}.")


SIGNED_INTEGER_FORMATS = "bhilq"
UNSIGNED_INTEGER_FORMATS = "BHILQ"

SIZE_TO_SIGNED_INTEGER_FORMAT = {
    struct.calcsize(signed_integer_format): signed_integer_format
    for signed_integer_format in SIGNED_INTEGER_FORMATS
}

SIZE_TO_UNSIGNED_INTEGER_FORMAT = {
    struct.calcsize(unsigned_integer_format): unsigned_integer_format
    for unsigned_integer_format in UNSIGNED_INTEGER_FORMATS
}

try:
    class int8(SimpleData[int], format=SIZE_TO_SIGNED_INTEGER_FORMAT[1]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class uint8(SimpleData[int], format=SIZE_TO_UNSIGNED_INTEGER_FORMAT[1]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class int16(SimpleData[int], format=SIZE_TO_SIGNED_INTEGER_FORMAT[2]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class uint16(SimpleData[int], format=SIZE_TO_UNSIGNED_INTEGER_FORMAT[2]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class int32(SimpleData[int], format=SIZE_TO_SIGNED_INTEGER_FORMAT[4]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class uint32(SimpleData[int], format=SIZE_TO_UNSIGNED_INTEGER_FORMAT[4]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class int64(SimpleData[int], format=SIZE_TO_SIGNED_INTEGER_FORMAT[8]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

    class uint64(SimpleData[int], format=SIZE_TO_UNSIGNED_INTEGER_FORMAT[8]):
        def __init__(self, value: int = 0) -> None:
            super().__init__(value)

except KeyError as error:
    raise OSError("Can not find all integer types.") from error

BITS_TO_SIGNED_TYPE = {
    signed_type.bits: signed_type for signed_type in (int8, int16, int32, int64)
}

BITS_TO_UNSIGNED_TYPE = {
    unsigned_type.bits: unsigned_type for unsigned_type in (uint8, uint16, uint32, uint64)
}


def get_int_type(bits: int, signed: bool = False) -> SimpleData[int]:
    try:
        if signed:
            return BITS_TO_SIGNED_TYPE[bits]

        else:
            return BITS_TO_UNSIGNED_TYPE[bits]

    except KeyError:
        prefix = "" if signed else "un"

        raise LookupError(f"Can not find {prefix}signed type with size of {bits} bits.") from None


get_ptr_type = get_int_type
get_size_type = get_int_type


class boolean(SimpleData[bool], format="?"):
    def __init__(self, value: bool = False) -> None:
        super().__init__(value)


class char(SimpleData[bytes], format="c"):
    def __init__(self, value: bytes = NULL_BYTE) -> None:
        super().__init__(value)


class float32(SimpleData[float], format="f"):
    def __init__(self, value: float = 0.0) -> None:
        super().__init__(value)


class float64(SimpleData[float], format="d"):
    def __init__(self, value: float = 0.0) -> None:
        super().__init__(value)


class Marker:
    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        info = {"name": repr(self.name)}

        return make_repr(self, info)

    @property
    def name(self) -> str:
        return self._name


def marker(name: str) -> Marker:
    return Marker(name)


bool_t = marker("bool_t")
char_t = marker("char_t")

int8_t = marker("int8_t")
uint8_t = marker("uint8_t")

int16_t = marker("int16_t")
uint16_t = marker("uint16_t")

int32_t = marker("int32_t")
uint32_t = marker("uint32_t")

int64_t = marker("int64_t")
uint64_t = marker("uint64_t")

int_size_t = marker("int_size_t")
uint_size_t = marker("uint_size_t")

int_ptr_t = marker("int_ptr_t")
uint_ptr_t = marker("uint_ptr_t")

float32_t = marker("float32_t")
float64_t = marker("float64_t")

byte_t = marker("byte_t")
ubyte_t = marker("ubyte_t")

short_t = marker("short_t")
ushort_t = marker("ushort_t")

int_t = marker("int_t")
uint_t = marker("uint_t")

long_t = marker("long_t")
ulong_t = marker("ulong_t")

longlong_t = marker("longlong_t")
ulonglong_t = marker("ulonglong_t")

float_t = marker("float_t")
double_t = marker("double_t")


class TypeFinder:
    def __init__(self, bits: int) -> None:
        byte_type = int8
        ubyte_type = uint8
        short_type = int16
        ushort_type = uint16

        if bits >= 32:
            int_type = int32
            uint_type = uint32

        else:
            int_type = int16
            uint_type = uint16

        if bits >= 64:
            long_type = int64
            ulong_type = uint64

        else:
            long_type = int32
            ulong_type = uint32

        longlong_type = int64
        ulonglong_type = uint64

        self._types: Dict[Marker, Type[Data]] = {
            bool_t: boolean,
            char_t: char,
            int8_t: int8,
            uint8_t: uint8,
            int16_t: int16,
            uint16_t: uint16,
            int32_t: int32,
            uint32_t: uint32,
            int64_t: int64,
            uint64_t: uint64,
            float32_t: float32,
            float64_t: float64,
            int_size_t: get_size_type(bits, signed=True),
            uint_size_t: get_size_type(bits, signed=False),
            int_ptr_t: get_ptr_type(bits, signed=True),
            uint_ptr_t: get_ptr_type(bits, signed=False),
            byte_t: byte_type,
            ubyte_t: ubyte_type,
            short_t: short_type,
            ushort_t: ushort_type,
            int_t: int_type,
            uint_t: uint_type,
            long_t: long_type,
            ulong_t: ulong_type,
            longlong_t: longlong_type,
            ulonglong_t: ulonglong_type,
            float_t: float32,
            double_t: float64,
        }

    def get_types(self) -> Dict[Marker, SimpleData]:
        return self._types

    types = property(get_types)

    def get_type(self, marker: Marker) -> SimpleData:
        if marker in self.types:
            return self.types[marker]

        raise LookupError(f"Can not find type for {marker!r}.")


class MarkedMeta(type):
    def __new__(
        meta_cls, cls_name: str, bases: Tuple[Type[Any], ...], cls_dict: Dict[str, Any]
    ) -> "MarkedMeta":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        markers: Dict[str, Marker] = {}

        for base in reversed(cls.mro()):
            annotations = get_type_hints(base)

            for _, annotation in annotations.items():
                if not isinstance(annotation, Marker):
                    raise TypeError("Unexpected annotations in struct or union.")

            markers.update(annotations)

        cls.MARKERS = markers

        return cls


class StructMeta(type):
    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        *,
        name: Optional[str] = None,
    ) -> "StructMeta":
        if name is None:
            name = cls_name

        cls = super().__new__(meta_cls, cls_name, bases, cls_dict)

        members: Dict[str, Type[Data]] = {}

        for base in reversed(cls.mro()):
            annotations = get_type_hints(base)

            for _, annotation in annotations.items():
                if not issubclass(annotation, Data):
                    raise TypeError("Unexpected annotations in struct or union.")

            members.update(annotations)

        format = concat(member.format for member in members.values())

        cls.members = members

        cls.name = name
        cls.format = format
        cls.size = struct.calcsize(format)
        cls.bytes = cls.size
        cls.bits = cls.bytes * BYTE_BITS

        return cls

    def __str__(cls) -> str:
        return cls.name

    def __repr__(cls) -> str:
        info = {"name": repr(cls.name), "size": cls.size}

        return make_repr(cls, info, name=f"struct {cls.__name__}")


class MarkedStruct(metaclass=MarkedMeta):
    pass


class MarkedUnion(metaclass=MarkedMeta):
    pass


class Struct(metaclass=StructMeta):
    pass
