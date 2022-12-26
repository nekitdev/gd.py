from struct import calcsize as size

__all__ = (
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

NATIVE: Final[str] = "="

I8_SIZE: Final[int] = size(NATIVE + I8)
U8_SIZE: Final[int] = size(NATIVE + U8)
I16_SIZE: Final[int] = size(NATIVE + I16)
U16_SIZE: Final[int] = size(NATIVE + U16)
I32_SIZE: Final[int] = size(NATIVE + I32)
U32_SIZE: Final[int] = size(NATIVE + U32)
I64_SIZE: Final[int] = size(NATIVE + I64)
U64_SIZE: Final[int] = size(NATIVE + U64)

F32_SIZE: Final[int] = size(NATIVE + F32)
F64_SIZE: Final[int] = size(NATIVE + F64)

HALF_BYTE: Final[int] = 0xF
HALF_BITS: Final[int] = HALF_BYTE.bit_length()

BYTE: Final[int] = 0xFF
BITS: Final[int] = BYTE.bit_length()

DOUBLE_BITS: Final[int] = BITS + BITS

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
