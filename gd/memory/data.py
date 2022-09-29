from abc import abstractmethod
from typing import Any, Optional, Type, TypeVar

from attrs import field, frozen
from typing_extensions import Never, Protocol, runtime_checkable

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
from gd.memory.constants import ZERO_SIZE
from gd.memory.state import AbstractState
from gd.platform import PlatformConfig

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
    "Ref",
    "MutRef",
    "ArrayData",
    "MutArrayData",
    "PointerData",
    "MutPointerData",
    "StructData",
    "UnionData",
)

T = TypeVar("T")

D = TypeVar("D", bound="AnyData")


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

    def copy(self: D) -> D:
        return type(self)()


AnyData = Data[Any]


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


@frozen()
class Void(Data[None]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        return None

    def write(
        self, state: AbstractState, address: int, value: None, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        pass

    def compute_size(self, config: PlatformConfig) -> int:
        return ZERO_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return ZERO_SIZE


# import cycle solution
from gd.memory.arrays import Array

UNSIZED_ARRAY = "array is unsized"

AD = TypeVar("AD", bound="AnyArrayData")


@frozen()
class ArrayData(Data[Array[T]]):
    type: Data[T] = field()
    length: Optional[int] = field(default=None)

    array_type: Type[Array[T]] = field(default=Array[T], repr=False)

    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> Array[T]:
        return self.array_type(state, address, self.type, self.length, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: Array[T],
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        length = self.length

        if length is None:
            raise TypeError(UNSIZED_ARRAY)

        return self.type.compute_size(config) * length

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.type.compute_alignment(config)

    def copy(self: AD) -> AD:
        return type(self)(self.type, self.length, self.array_type)


AnyArrayData = ArrayData[Any]


# import cycle solution
from gd.memory.arrays import MutArray

MAD = TypeVar("MAD", bound="AnyMutArrayData")


@frozen()
class MutArrayData(Data[MutArray[T]]):
    type: Data[T] = field()
    length: Optional[int] = field(default=None)

    array_type: Type[MutArray[T]] = field(default=MutArray[T], repr=False)

    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> MutArray[T]:
        return self.array_type(state, address, self.type, self.length, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: MutArray[T],
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        length = self.length

        if length is None:
            raise TypeError(UNSIZED_ARRAY)

        return self.type.compute_size(config) * length

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.type.compute_alignment(config)

    def copy(self: MAD) -> MAD:
        return type(self)(self.type, self.length, self.array_type)


AnyMutArrayData = MutArrayData[Any]


# import cycle solution
from gd.memory.base import Struct

S = TypeVar("S", bound="Struct")

SD = TypeVar("SD", bound="AnyStructData")


@frozen()
class StructData(Data[S]):
    struct_type: Type[S] = field()

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> S:
        return self.struct_type(state, address, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: S,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.struct_type.reconstruct(config).SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.struct_type.reconstruct(config).ALIGNMENT

    def copy(self: SD) -> SD:
        return type(self)(self.struct_type)


AnyStructData = StructData[Struct]


# import cycle solution
from gd.memory.base import Union as UnionType

U = TypeVar("U", bound="UnionType")

UD = TypeVar("UD", bound="AnyUnionData")


@frozen()
class UnionData(Data[U]):
    union_type: Type[U] = field()

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> U:
        return self.union_type(state, address, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: U,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.union_type.reconstruct(config).SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.union_type.reconstruct(config).ALIGNMENT

    def copy(self: UD) -> UD:
        return type(self)(self.union_type)


AnyUnionData = UnionData[UnionType]


# import cycle solution
from gd.memory.pointers import Pointer

PD = TypeVar("PD", bound="AnyPointerData")


@frozen()
class PointerData(Data[Pointer[T]]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[Pointer[T]] = field(default=Pointer[T], repr=False)

    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> Pointer[T]:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: Pointer[T],
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)

    def copy(self: PD) -> PD:
        return type(self)(self.type, self.pointer_type, self.internal_pointer_type)


AnyPointerData = PointerData[Any]


# import cycle solution
from gd.memory.pointers import MutPointer

MPD = TypeVar("MPD", bound="AnyMutPointerData")


@frozen()
class MutPointerData(Data[MutPointer[T]]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[MutPointer[T]] = field(default=MutPointer[T], repr=False)

    def read(
        self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> MutPointer[T]:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order)

    def write(
        self,
        state: AbstractState,
        address: int,
        value: MutPointer[T],
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        pass  # do nothing

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)

    def copy(self: MPD) -> MPD:
        return type(self)(self.type, self.pointer_type, self.internal_pointer_type)


AnyMutPointerData = MutPointerData[Any]


IMMUTABLE_REFERENCE = "the reference is immutable"

R = TypeVar("R", bound="AnyRef")


@frozen()
class Ref(Data[T]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[Pointer[T]] = field(default=Pointer[T])

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> T:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order).value

    def write(
        self,
        state: AbstractState,
        address: int,
        value: T,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> Never:
        raise TypeError(IMMUTABLE_REFERENCE)

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)

    def copy(self: R) -> R:
        return type(self)(self.type, self.pointer_type, self.internal_pointer_type)


AnyRef = Ref[Any]


MR = TypeVar("MR", bound="AnyMutRef")


@frozen()
class MutRef(Data[T]):
    type: Data[T] = field()
    pointer_type: Data[int] = field(factory=USize)

    internal_pointer_type: Type[MutPointer[T]] = field(default=MutPointer[T], repr=False)

    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> T:
        return self.internal_pointer_type(state, address, self.type, self.pointer_type, order).value

    def write(
        self,
        state: AbstractState,
        address: int,
        value: T,
        order: ByteOrder = ByteOrder.NATIVE,
    ) -> None:
        self.internal_pointer_type(
            state, address, self.type, self.pointer_type, order
        ).value = value

    def compute_size(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_size(config)

    def compute_alignment(self, config: PlatformConfig) -> int:
        return self.pointer_type.compute_alignment(config)

    def copy(self: MR) -> MR:
        return type(self)(self.type, self.pointer_type, self.internal_pointer_type)


AnyMutRef = MutRef[Any]
