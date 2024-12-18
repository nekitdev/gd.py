from struct import calcsize as size
from typing import Final

__all__ = (
    # bool size
    "BOOL_SIZE",
    # int sizes
    "I8_SIZE",
    "U8_SIZE",
    "I16_SIZE",
    "U16_SIZE",
    "I32_SIZE",
    "U32_SIZE",
    "I64_SIZE",
    "U64_SIZE",
    # float sizes
    "F32_SIZE",
    "F64_SIZE",
    # bool bits
    "BOOL_BITS",
    # int bits
    "I8_BITS",
    "U8_BITS",
    "I16_BITS",
    "U16_BITS",
    "I32_BITS",
    "U32_BITS",
    "I64_BITS",
    "U64_BITS",
    # float bits
    "F32_BITS",
    "F64_BITS",
    # bytes
    "BYTE",
    # bits
    "SIZE_BITS",
)

BOOL: Final = "?"
"""The `bool` type."""

I8: Final = "b"
"""The `i8` type."""

U8: Final = "B"
"""The `u8` type."""

I16: Final = "h"
"""The `i16` type."""

U16: Final = "H"
"""The `u16` type."""

I32: Final = "i"
"""The `i32` type."""

U32: Final = "I"
"""The `u32` type."""

I64: Final = "q"
"""The `i64` type."""

U64: Final = "Q"
"""The `u64` type."""

F32: Final = "f"
"""The `f32` type."""

F64: Final = "d"
"""The `f64` type."""

STANDARD: Final = "="
"""The standard size and native byte order specification."""


def standard_size(type: str) -> int:
    """Returns the standard size of the given type.

    Arguments:
        type: The type to get the size of.

    Returns:
        The size of the type.
    """
    return size(STANDARD + type)


BOOL_SIZE: Final = standard_size(BOOL)
"""The size of the `bool` type."""

I8_SIZE: Final = standard_size(I8)
"""The size of the `i8` type."""

U8_SIZE: Final = standard_size(U8)
"""The size of the `u8` type."""

I16_SIZE: Final = standard_size(I16)
"""The size of the `i16` type."""

U16_SIZE: Final = standard_size(U16)
"""The size of the `u16` type."""

I32_SIZE: Final = standard_size(I32)
"""The size of the `i32` type."""

U32_SIZE: Final = standard_size(U32)
"""The size of the `u32` type."""

I64_SIZE: Final = standard_size(I64)
"""The size of the `i64` type."""

U64_SIZE: Final = standard_size(U64)
"""The size of the `u64` type."""

F32_SIZE: Final = standard_size(F32)
"""The size of the `f32` type."""

F64_SIZE: Final = standard_size(F64)
"""The size of the `f64` type."""

BYTE: Final = 0xFF
"""The byte value."""

SIZE_BITS: Final = BYTE.bit_length()
"""The multiplier for computing type size in bits."""

BOOL_BITS: Final = BOOL_SIZE * SIZE_BITS
"""The size of the `bool` type in bits."""

I8_BITS: Final = I8_SIZE * SIZE_BITS
"""The size of the `i8` type in bits."""

U8_BITS: Final = U8_SIZE * SIZE_BITS
"""The size of the `u8` type in bits."""

I16_BITS: Final = I16_SIZE * SIZE_BITS
"""The size of the `i16` type in bits."""

U16_BITS: Final = U16_SIZE * SIZE_BITS
"""The size of the `u16` type in bits."""

I32_BITS: Final = I32_SIZE * SIZE_BITS
"""The size of the `i32` type in bits."""

U32_BITS: Final = U32_SIZE * SIZE_BITS
"""The size of the `u32` type in bits."""

I64_BITS: Final = I64_SIZE * SIZE_BITS
"""The size of the `i64` type in bits."""

U64_BITS: Final = U64_SIZE * SIZE_BITS
"""The size of the `u64` type in bits."""

F32_BITS: Final = F32_SIZE * SIZE_BITS
"""The size of the `f32` type in bits."""

F64_BITS: Final = F64_SIZE * SIZE_BITS
"""The size of the `f64` type in bits."""
