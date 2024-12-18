from __future__ import annotations

from struct import pack, unpack
from typing import Callable, TypeVar

from iters.utils import unpack_unary_tuple

from gd.binary.constants import BOOL, F32, F64, I8, I16, I32, I64, U8, U16, U32, U64
from gd.binary.enums import ByteOrder

__all__ = (
    # to
    "To",
    # from
    "From",
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
)

from mypy_extensions import DefaultArg

T = TypeVar("T")


To = Callable[[bytes, DefaultArg(ByteOrder)], T]
From = Callable[[T, DefaultArg(ByteOrder)], bytes]


def create_to_int(type: str) -> To[int]:
    """Creates the `to_int` function that unpacks binary data to integers.

    Arguments:
        type: The integer type to use.

    Returns:
        The `to_int` function.
    """

    def to_int(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> int:
        return unpack_unary_tuple(unpack(order.value + type, data))

    return to_int


def create_from_int(type: str) -> From[int]:
    """Creates the `from_int` function that packs integers to binary data.

    Arguments:
        type: The integer type to use.

    Returns:
        The `from_int` function.
    """

    def from_int(value: int, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + type, value)

    return from_int


def create_to_float(type: str) -> To[float]:
    """Creates the `to_float` function that unpacks binary data to floats.

    Arguments:
        type: The float type to use.

    Returns:
        The `to_float` function.
    """

    def to_float(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> float:
        return unpack_unary_tuple(unpack(order.value + type, data))

    return to_float


def create_from_float(type: str) -> From[float]:
    """Creates the `from_float` function that packs floats to binary data.

    Arguments:
        type: The float type to use.

    Returns:
        The `from_float` function.
    """

    def from_float(value: float, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + type, value)

    return from_float


def create_to_bool(type: str) -> To[bool]:
    """Creates the `to_bool` function that unpacks binary data to bools.

    Arguments:
        type: The bool type to use.

    Returns:
        The `to_bool` function.
    """

    def to_bool(data: bytes, order: ByteOrder = ByteOrder.DEFAULT) -> bool:
        return unpack_unary_tuple(unpack(order.value + type, data))

    return to_bool


def create_from_bool(type: str) -> From[bool]:
    """Creates the `from_bool` function that packs bools to binary data.

    Arguments:
        type: The bool type to use.

    Returns:
        The `from_bool` function.
    """

    def from_bool(value: bool, order: ByteOrder = ByteOrder.DEFAULT) -> bytes:
        return pack(order.value + type, value)

    return from_bool


to_bool = create_to_bool(BOOL)
"""The `to_bool` function that converts binary data to bools."""

to_i8 = create_to_int(I8)
"""The `to_i8` function that converts binary data to 8-bit signed integers."""

to_u8 = create_to_int(U8)
"""The `to_u8` function that converts binary data to 8-bit unsigned integers."""

to_i16 = create_to_int(I16)
"""The `to_i16` function that converts binary data to 16-bit signed integers."""

to_u16 = create_to_int(U16)
"""The `to_u16` function that converts binary data to 16-bit unsigned integers."""

to_i32 = create_to_int(I32)
"""The `to_i32` function that converts binary data to 32-bit signed integers."""

to_u32 = create_to_int(U32)
"""The `to_u32` function that converts binary data to 32-bit unsigned integers."""

to_i64 = create_to_int(I64)
"""The `to_i64` function that converts binary data to 64-bit signed integers."""

to_u64 = create_to_int(U64)
"""The `to_u64` function that converts binary data to 64-bit unsigned integers."""

to_f32 = create_to_float(F32)
"""The `to_f32` function that converts binary data to 32-bit floats."""

to_f64 = create_to_float(F64)
"""The `to_f64` function that converts binary data to 64-bit floats."""

from_bool = create_from_bool(BOOL)
"""The `from_bool` function that converts bools to binary data."""

from_i8 = create_from_int(I8)
"""The `from_i8` function that converts 8-bit signed integers to binary data."""

from_u8 = create_from_int(U8)
"""The `from_u8` function that converts 8-bit unsigned integers to binary data."""

from_i16 = create_from_int(I16)
"""The `from_i16` function that converts 16-bit signed integers to binary data."""

from_u16 = create_from_int(U16)
"""The `from_u16` function that converts 16-bit unsigned integers to binary data."""

from_i32 = create_from_int(I32)
"""The `from_i32` function that converts 32-bit signed integers to binary data."""

from_u32 = create_from_int(U32)
"""The `from_u32` function that converts 32-bit unsigned integers to binary data."""

from_i64 = create_from_int(I64)
"""The `from_i64` function that converts 64-bit signed integers to binary data."""

from_u64 = create_from_int(U64)
"""The `from_u64` function that converts 64-bit unsigned integers to binary data."""

from_f32 = create_from_float(F32)
"""The `from_f32` function that converts 32-bit floats to binary data."""

from_f64 = create_from_float(F64)
"""The `from_f64` function that converts 64-bit floats to binary data."""
