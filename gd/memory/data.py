from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, TypeVar

from attrs import frozen
from typing_extensions import Protocol, runtime_checkable

from gd.binary_constants import (
    BOOL_SIZE,
    F32_SIZE,
    F64_SIZE,
    I8_SIZE,
    I16_SIZE,
    I32_SIZE,
    I64_SIZE,
    U8_SIZE,
    U16_SIZE,
    U32_SIZE,
    U64_SIZE,
)
from gd.enums import ByteOrder
from gd.platform import PlatformConfig

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = (
    "I8",
    "U8",
    "I16",
    "U16",
    "I32",
    "U32",
    "I64",
    "U64",
    "ISize",
    "USize",
    "F32",
    "F64",
    "Bool",
    "Byte",
    "UByte",
    "Short",
    "UShort",
    "Int",
    "UInt",
    "Long",
    "ULong",
    "LongLong",
    "ULongLong",
    "Size",
    "Float",
    "Double",
)

T = TypeVar("T")


@runtime_checkable
class Data(Protocol[T]):
    @abstractmethod
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> T:
        ...

    @abstractmethod
    def write(
        self, state: AbstractState, address: int, value: T, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        ...

    @abstractmethod
    def compute_size(self, config: PlatformConfig) -> int:
        ...

    @abstractmethod
    def compute_alignment(self, config: PlatformConfig) -> int:
        ...


@frozen()
class I8(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_i8(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_i8(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I8_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I8_SIZE


@frozen()
class U8(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_u8(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_u8(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U8_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U8_SIZE


@frozen()
class I16(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_i16(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_i16(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I16_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I16_SIZE


@frozen()
class U16(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_u16(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_u16(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U16_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U16_SIZE


@frozen()
class I32(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_i32(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_i32(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I32_SIZE


@frozen()
class U32(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_u32(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_u32(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U32_SIZE


@frozen()
class I64(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_i64(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_i64(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I64_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I64_SIZE


@frozen()
class U64(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_u64(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_u64(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U64_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U64_SIZE


@frozen()
class ISize(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_isize(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_isize(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        size = {8: I8_SIZE, 16: I16_SIZE, 32: I32_SIZE, 64: I64_SIZE}

        return size[config.bits]

    def compute_alignment(self, config: PlatformConfig) -> int:
        alignment = {8: I8_SIZE, 16: I16_SIZE, 32: I32_SIZE, 64: I64_SIZE}

        return alignment[config.bits]


@frozen()
class USize(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_usize(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_usize(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        size = {8: U8_SIZE, 16: U16_SIZE, 32: U32_SIZE, 64: U64_SIZE}

        return size[config.bits]

    def compute_alignment(self, config: PlatformConfig) -> int:
        alignment = {8: U8_SIZE, 16: U16_SIZE, 32: U32_SIZE, 64: U64_SIZE}

        return alignment[config.bits]


@frozen()
class F32(Data[float]):
    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> float:
        return state.read_f32(address, order)

    def write(
        self, state: AbstractState, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_f32(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return F32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return F32_SIZE


@frozen()
class F64(Data[float]):
    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> float:
        return state.read_f64(address, order)

    def write(
        self, state: AbstractState, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_f64(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return F64_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return F64_SIZE


@frozen()
class Bool(Data[bool]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> bool:
        return state.read_bool(address, order)

    def write(
        self, state: AbstractState, address: int, value: bool, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_bool(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return BOOL_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return BOOL_SIZE


@frozen()
class Byte(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_byte(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_byte(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I8_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I8_SIZE


@frozen()
class UByte(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_ubyte(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_ubyte(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U8_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U8_SIZE


@frozen()
class Short(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_short(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_short(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I16_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I16_SIZE


@frozen()
class UShort(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_ushort(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_ushort(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U16_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U16_SIZE


@frozen()
class Int(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_int(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_int(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        if config.bits < 32:
            return I16_SIZE

        return I32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        if config.bits < 32:
            return I16_SIZE

        return I32_SIZE


@frozen()
class UInt(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_uint(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_uint(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        if config.bits < 32:
            return U16_SIZE

        return U32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        if config.bits < 32:
            return U16_SIZE

        return U32_SIZE


@frozen()
class Long(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_long(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_long(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        if config.bits > 32 and not config.platform.is_windows():
            return I64_SIZE

        return I32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        if config.bits > 32 and not config.platform.is_windows():
            return I64_SIZE

        return I32_SIZE


@frozen()
class ULong(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_ulong(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_ulong(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        if config.bits > 32 and not config.platform.is_windows():
            return U64_SIZE

        return U32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        if config.bits > 32 and not config.platform.is_windows():
            return U64_SIZE

        return U32_SIZE


@frozen()
class LongLong(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_longlong(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_longlong(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return I64_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return I64_SIZE


@frozen()
class ULongLong(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_ulonglong(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_ulonglong(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return U64_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return U64_SIZE


@frozen()
class Size(Data[int]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_size(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_size(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        size = {8: I8_SIZE, 16: I16_SIZE, 32: I32_SIZE, 64: I64_SIZE}

        return size[config.bits]

    def compute_alignment(self, config: PlatformConfig) -> int:
        size = {8: I8_SIZE, 16: I16_SIZE, 32: I32_SIZE, 64: I64_SIZE}

        return size[config.bits]


@frozen()
class Float(Data[float]):
    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> float:
        return state.read_float(address, order)

    def write(
        self, state: AbstractState, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_float(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return F32_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return F32_SIZE


@frozen()
class Double(Data[float]):
    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> float:
        return state.read_double(address, order)

    def write(
        self, state: AbstractState, address: int, value: float, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_double(address, value, order)

    def compute_size(self, config: PlatformConfig) -> int:
        return F64_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return F64_SIZE
