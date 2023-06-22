from struct import calcsize as size

from gd.enums import ByteOrder

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
    # bits
    "HALF_BYTE",
    "HALF_BITS",
    "BYTE",
    "BITS",
    "DOUBLE_BITS",
)

from typing_extensions import Final

BOOL: Final = "?"

I8: Final = "b"
U8: Final = "B"
I16: Final = "h"
U16: Final = "H"
I32: Final = "i"
U32: Final = "I"
I64: Final = "q"
U64: Final = "Q"

F32: Final = "f"
F64: Final = "d"

NATIVE: Final = ByteOrder.NATIVE.value

BOOL_SIZE: Final = size(NATIVE + BOOL)

I8_SIZE: Final = size(NATIVE + I8)
U8_SIZE: Final = size(NATIVE + U8)
I16_SIZE: Final = size(NATIVE + I16)
U16_SIZE: Final = size(NATIVE + U16)
I32_SIZE: Final = size(NATIVE + I32)
U32_SIZE: Final = size(NATIVE + U32)
I64_SIZE: Final = size(NATIVE + I64)
U64_SIZE: Final = size(NATIVE + U64)

F32_SIZE: Final = size(NATIVE + F32)
F64_SIZE: Final = size(NATIVE + F64)

HALF_BYTE: Final = 0xF
HALF_BITS: Final = HALF_BYTE.bit_length()

BYTE: Final = 0xFF
BITS: Final = BYTE.bit_length()

DOUBLE_BITS: Final = BITS + BITS

BOOL_BITS: Final = BOOL_SIZE * BITS

I8_BITS: Final = I8_SIZE * BITS
U8_BITS: Final = U8_SIZE * BITS
I16_BITS: Final = I16_SIZE * BITS
U16_BITS: Final = U16_SIZE * BITS
I32_BITS: Final = I32_SIZE * BITS
U32_BITS: Final = U32_SIZE * BITS
I64_BITS: Final = I64_SIZE * BITS
U64_BITS: Final = U64_SIZE * BITS

F32_BITS: Final = F32_SIZE * BITS
F64_BITS: Final = F64_SIZE * BITS
