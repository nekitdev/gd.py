from __future__ import annotations

from struct import pack, unpack
from typing import TYPE_CHECKING

from iters.utils import unpack_unary_tuple

from gd.binary_constants import BOOL, F32, F64, I8, I16, I32, I64, U8, U16, U32, U64
from gd.enums import ByteOrder

if TYPE_CHECKING:
    from typing_aliases import Binary

__all__ = (
    # from bool
    "from_bool",
    # from int
    "from_i8",
    "from_u8",
    "from_i16",
    "from_u16",
    "from_i32",
    "from_u32",
    "from_i64",
    "from_u64",
    # from float
    "from_f32",
    "from_f64",
    # to bool
    "to_bool",
    # to int
    "to_i8",
    "to_u8",
    "to_i16",
    "to_u16",
    "to_i32",
    "to_u32",
    "to_i64",
    "to_u64",
    # to float
    "to_f32",
    "to_f64",
)


def create_from_int(format: str) -> Binary[bytes, ByteOrder, int]:
    def from_int(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return unpack_unary_tuple(unpack(order.value + format, data))

    return from_int


def create_to_int(format: str) -> Binary[int, ByteOrder, bytes]:
    def to_int(value: int, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_int


def create_from_float(format: str) -> Binary[bytes, ByteOrder, float]:
    def from_float(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> float:
        return unpack_unary_tuple(unpack(order.value + format, data))

    return from_float


def create_to_float(format: str) -> Binary[float, ByteOrder, bytes]:
    def to_float(value: float, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + format, value)

    return to_float


def create_from_bool(format: str) -> Binary[bytes, ByteOrder, bool]:
    def from_bool(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> bool:
        return unpack_unary_tuple(unpack(order.value + format, data))

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
