from __future__ import annotations

from struct import pack, unpack
from typing import Any, Generic, TypeVar

from attrs import Attribute, field, frozen
from iters.utils import unpack_unary_tuple
from typing_aliases import Binary

from gd.binary import BinaryReader, BinaryWriter
from gd.binary_constants import (
    BOOL,
    F32,
    F32_SIZE,
    F64,
    F64_SIZE,
    I8,
    I8_SIZE,
    I16,
    I16_SIZE,
    I32,
    I32_SIZE,
    I64,
    I64_SIZE,
    U8,
    U8_SIZE,
    U16,
    U16_SIZE,
    U32,
    U32_SIZE,
    U64,
    U64_SIZE,
)
from gd.enums import ByteOrder

__all__ = (
    # reader, writer
    "Reader",
    "Writer",
    # from ints
    "from_i8",
    "from_u8",
    "from_i16",
    "from_u16",
    "from_i32",
    "from_u32",
    "from_i64",
    "from_u64",
    # from floats
    "from_f32",
    "from_f64",
    # to ints
    "to_i8",
    "to_u8",
    "to_i16",
    "to_u16",
    "to_i32",
    "to_u32",
    "to_i64",
    "to_u64",
    # to floats
    "to_f32",
    "to_f64",
)


def create_from_int(format: str) -> Binary[bytes, ByteOrder, int]:
    def from_int(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return unpack_unary_tuple(unpack(order.value + format, data))  # type: ignore

    return from_int


def create_to_int(format: str) -> Binary[int, ByteOrder, bytes]:
    def to_int(value: int, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_int


def create_from_float(format: str) -> Binary[bytes, ByteOrder, float]:
    def from_float(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> float:
        return unpack_unary_tuple(unpack(order.value + format, data))  # type: ignore

    return from_float


def create_to_float(format: str) -> Binary[float, ByteOrder, bytes]:
    def to_float(value: float, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_float


def create_from_bool(format: str) -> Binary[bytes, ByteOrder, bool]:
    def from_bool(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> bool:
        return unpack_unary_tuple(unpack(order.value + format, data))  # type: ignore

    return from_bool


def create_to_bool(format: str) -> Binary[bool, ByteOrder, bytes]:
    def to_bool(value: bool, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_bool


from_bool = create_from_bool(BOOL)

from_i8 = create_from_int(I8)
from_u8 = create_from_int(U8)
from_i16 = create_from_int(I16)
from_u16 = create_from_int(U16)
from_i32 = create_from_int(I32)
from_u32 = create_from_int(U32)
from_i64 = create_from_int(I64)
from_u64 = create_from_int(U64)

from_f32 = create_from_float(F32)
from_f64 = create_from_float(F64)

to_bool = create_to_bool(BOOL)

to_i8 = create_to_int(I8)
to_u8 = create_to_int(U8)
to_i16 = create_to_int(I16)
to_u16 = create_to_int(U16)
to_i32 = create_to_int(I32)
to_u32 = create_to_int(U32)
to_i64 = create_to_int(I64)
to_u64 = create_to_int(U64)

to_f32 = create_to_float(F32)
to_f64 = create_to_float(F64)

R = TypeVar("R", bound=BinaryReader)
W = TypeVar("W", bound=BinaryWriter)

NATIVE_NOT_ALLOWED = "`native` byte order is not allowed"


@frozen()
class Reader(Generic[R]):
    reader: R = field()
    order: ByteOrder = field(default=ByteOrder.DEFAULT)

    @order.validator
    def check_order(self, attribute: Attribute[ByteOrder], order: ByteOrder) -> None:
        if order.is_native():
            raise ValueError(NATIVE_NOT_ALLOWED)

    def read_i8(self) -> int:
        return from_i8(self.read(I8_SIZE), self.order)

    def read_u8(self) -> int:
        return from_u8(self.read(U8_SIZE), self.order)

    def read_i16(self) -> int:
        return from_i16(self.read(I16_SIZE), self.order)

    def read_u16(self) -> int:
        return from_u16(self.read(U16_SIZE), self.order)

    def read_i32(self) -> int:
        return from_i32(self.read(I32_SIZE), self.order)

    def read_u32(self) -> int:
        return from_u32(self.read(U32_SIZE), self.order)

    def read_i64(self) -> int:
        return from_i64(self.read(I64_SIZE), self.order)

    def read_u64(self) -> int:
        return from_u64(self.read(U64_SIZE), self.order)

    def read_f32(self) -> float:
        return from_f32(self.read(F32_SIZE), self.order)

    def read_f64(self) -> float:
        return from_f64(self.read(F64_SIZE), self.order)

    def read(self, size: int) -> bytes:
        return self.reader.read(size)


AnyReader = Reader[Any]


@frozen()
class Writer(Generic[W]):
    writer: W = field()
    order: ByteOrder = field(default=ByteOrder.DEFAULT)

    @order.validator
    def check_order(self, attribute: Attribute[ByteOrder], order: ByteOrder) -> None:
        if order.is_native():
            raise ValueError(NATIVE_NOT_ALLOWED)

    def write_i8(self, value: int) -> None:
        self.write(to_i8(value, self.order))

    def write_u8(self, value: int) -> None:
        self.write(to_u8(value, self.order))

    def write_i16(self, value: int) -> None:
        self.write(to_i16(value, self.order))

    def write_u16(self, value: int) -> None:
        self.write(to_u16(value, self.order))

    def write_i32(self, value: int) -> None:
        self.write(to_i32(value, self.order))

    def write_u32(self, value: int) -> None:
        self.write(to_u32(value, self.order))

    def write_i64(self, value: int) -> None:
        self.write(to_i64(value, self.order))

    def write_u64(self, value: int) -> None:
        self.write(to_u64(value, self.order))

    def write_f32(self, value: float) -> None:
        self.write(to_f32(value, self.order))

    def write_f64(self, value: float) -> None:
        self.write(to_f64(value, self.order))

    def write(self, data: bytes) -> None:
        self.writer.write(data)


try:
    from _gd import Reader, Writer  # noqa

except ImportError:
    pass
