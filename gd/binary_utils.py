from struct import calcsize as size
from struct import pack, unpack
from typing import BinaryIO, Generic, TypeVar

from attrs import frozen
from typing_extensions import Final

from gd.enums import ByteOrder
from gd.typing import Binary

__all__ = ("Reader", "Writer")

I8: Final[str] = "b"
U8: Final[str] = "B"
I16: Final[str] = "h"
U16: Final[str] = "H"
I32: Final[str] = "i"
U32: Final[str] = "I"
I64: Final[str] = "q"
U64: Final[str] = "Q"

F32: Final[str] = "f"
F64: Final[str] = "d"

I8_SIZE: Final[int] = size(I8)
U8_SIZE: Final[int] = size(U8)
I16_SIZE: Final[int] = size(I16)
U16_SIZE: Final[int] = size(U16)
I32_SIZE: Final[int] = size(I32)
U32_SIZE: Final[int] = size(U32)
I64_SIZE: Final[int] = size(I64)
U64_SIZE: Final[int] = size(U64)

F32_SIZE: Final[int] = size(F32)
F64_SIZE: Final[int] = size(F64)

BITS: Final[int] = 8

I8_BITS: Final[int] = I8_SIZE * BITS
U8_BITS: Final[int] = U8_SIZE * BITS
I16_BITS: Final[int] = I16_SIZE * BITS
U16_BITS: Final[int] = U16_SIZE * BITS
I32_BITS: Final[int] = I32_SIZE * BITS
U32_BITS: Final[int] = U32_SIZE * BITS
I64_BITS: Final[int] = I64_SIZE * BITS
U64_BITS: Final[int] = U64_SIZE * BITS

F32_BITS: Final[int] = F32_SIZE * BITS
F64_BITS: Final[int] = F64_SIZE * BITS


def create_from_int(format: str) -> Binary[bytes, ByteOrder, int]:
    def from_int(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        result, = unpack(order.value + format, data)

        return result

    return from_int


def create_to_int(format: str) -> Binary[int, ByteOrder, bytes]:
    def to_int(value: int, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_int


def create_from_float(format: str) -> Binary[bytes, ByteOrder, float]:
    def from_float(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> float:
        result, = unpack(order.value + format, data)

        return result

    return from_float


def create_to_float(format: str) -> Binary[float, ByteOrder, bytes]:
    def to_float(value: float, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_float


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


B = TypeVar("B", bound=BinaryIO)


@frozen()
class Reader(Generic[B]):
    reader: B

    def read_i8(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_i8(self.read(I8_SIZE), order)

    def read_u8(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_u8(self.read(U8_SIZE), order)

    def read_i16(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_i16(self.read(I16_SIZE), order)

    def read_u16(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_u16(self.read(U16_SIZE), order)

    def read_i32(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_i32(self.read(I32_SIZE), order)

    def read_u32(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_u32(self.read(U32_SIZE), order)

    def read_i64(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_i64(self.read(I64_SIZE), order)

    def read_u64(self, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return from_u64(self.read(U64_SIZE), order)

    def read_f32(self, order: ByteOrder = ByteOrder.DEFAULT) -> float:
        return from_f32(self.read(F32_SIZE), order)

    def read_f64(self, order: ByteOrder = ByteOrder.DEFAULT) -> float:
        return from_f64(self.read(F64_SIZE), order)

    def read(self, size: int) -> bytes:
        return self.reader.read(size)


@frozen()
class Writer(Generic[B]):
    writer: B

    def write_i8(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_i8(value, order))

    def write_u8(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_u8(value, order))

    def write_i16(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_i16(value, order))

    def write_u16(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_u16(value, order))

    def write_i32(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_i32(value, order))

    def write_u32(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_u32(value, order))

    def write_i64(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_i64(value, order))

    def write_u64(self, value: int, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_u64(value, order))

    def write_f32(self, value: float, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_f32(value, order))

    def write_f64(self, value: float, order: ByteOrder = ByteOrder.DEFAULT) -> None:
        self.write(to_f64(value, order))

    def write(self, data: bytes) -> None:
        self.writer.write(data)
