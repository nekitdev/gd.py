from __future__ import annotations

from abc import abstractmethod
from typing import Any, Generic, Iterator, Optional, Tuple, Type, TypeVar, Union, overload

from attrs import define, field
from typing_extensions import Never, Protocol

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
from gd.memory.constants import VOID_SIZE
from gd.memory.state import AbstractState
from gd.platform import PlatformConfig
from gd.typing import StringDict, is_instance

__all__ = (
    "Field",
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
    "ArrayField",
    "MutArrayField",
    "PointerField",
    "MutPointerField",
    "StructField",
    "UnionField",
)

T = TypeVar("T")


class FieldProtocol(Protocol[T]):
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


FROZEN_FIELD = "this field is frozen"
CAN_NOT_DELETE_FIELDS = "can not delete fields"

DEFAULT_OFFSET = 0
DEFAULT_FROZEN = False


B = TypeVar("B", bound="Base")

F = TypeVar("F", bound="AnyField")


@define()
class Field(FieldProtocol[T]):
    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

    def copy(self: F) -> F:
        return type(self)(self.offset)


AnyField = Field[Any]


def fetch_fields_iterator(base: Type[B]) -> Iterator[Tuple[str, AnyField]]:
    for type in reversed(base.mro()):
        for name, value in vars(type).items():
            if is_instance(value, Field):
                yield (name, value)


def fetch_fields(base: Type[B]) -> StringDict[AnyField]:
    return dict(fetch_fields_iterator(base))


@define()
class ActualField(Generic[T]):
    field: Field[T]

    @overload
    def __get__(self, instance: None, type: Optional[Type[B]] = ...) -> Field[T]:
        ...

    @overload
    def __get__(self, instance: B, type: Optional[Type[B]]) -> T:
        ...

    def __get__(self, instance: Optional[B], type: Optional[Type[B]] = None) -> Union[Field[T], T]:
        if instance is None:
            return self.field

        if is_instance(instance, Base):
            return self.field.read(
                instance.state, instance.address + self.field.offset, instance.order
            )

        return self.field

    def __set__(self, instance: B, value: T) -> None:
        self.field.write(
            instance.state, instance.address + self.field.offset, value, instance.order
        )

    def __delete__(self, instance: B) -> Never:
        raise AttributeError(CAN_NOT_DELETE_FIELDS)


@define()
class I8(Field[int]):
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


@define()
class U8(Field[int]):
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


@define()
class I16(Field[int]):
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


@define()
class U16(Field[int]):
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


@define()
class I32(Field[int]):
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


@define()
class U32(Field[int]):
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


@define()
class I64(Field[int]):
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


@define()
class U64(Field[int]):
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


@define()
class ISize(Field[int]):
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


@define()
class USize(Field[int]):
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


class F32(Field[float]):
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


class F64(Field[float]):
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


class Bool(Field[bool]):
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


class Byte(Field[int]):
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


class UByte(Field[int]):
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


class Short(Field[int]):
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


class UShort(Field[int]):
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


class Int(Field[int]):
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


class UInt(Field[int]):
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


class Long(Field[int]):
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


class ULong(Field[int]):
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


class LongLong(Field[int]):
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


class ULongLong(Field[int]):
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


@define()
class Size(Field[int]):
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


class Float(Field[float]):
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


class Double(Field[float]):
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


class Void(Field[None]):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> None:
        return None

    def write(
        self, state: AbstractState, address: int, value: None, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        pass

    def compute_size(self, config: PlatformConfig) -> int:
        return VOID_SIZE

    def compute_alignment(self, config: PlatformConfig) -> int:
        return VOID_SIZE


# import cycle solution
from gd.memory.arrays import Array

UNSIZED_ARRAY = "array is unsized"

AF = TypeVar("AF", bound="AnyArrayField")


@define()
class ArrayField(Field[Array[T]]):
    type: Field[T] = field()
    length: Optional[int] = field(default=None)

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

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

    def copy(self: AF) -> AF:
        return type(self)(self.type, self.length, self.offset, self.array_type)


AnyArrayField = ArrayField[Any]


# import cycle solution
from gd.memory.arrays import MutArray

MAF = TypeVar("MAF", bound="AnyMutArrayField")


@define()
class MutArrayField(Field[MutArray[T]]):
    type: Field[T] = field()
    length: Optional[int] = field(default=None)

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

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

    def copy(self: MAF) -> MAF:
        return type(self)(self.type, self.length, self.offset, self.array_type)


AnyMutArrayField = MutArrayField[Any]


# import cycle solution
from gd.memory.base import Struct

S = TypeVar("S", bound="Struct")

SF = TypeVar("SF", bound="AnyStructField")


@define()
class StructField(Field[S]):
    struct_type: Type[S] = field()

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

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

    def copy(self: SF) -> SF:
        return type(self)(self.struct_type, self.offset)


AnyStructField = StructField[Struct]


# import cycle solution
from gd.memory.base import Union as UnionType

U = TypeVar("U", bound="UnionType")

UF = TypeVar("UF", bound="AnyUnionField")


@define()
class UnionField(Field[U]):
    union_type: Type[U] = field()

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

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

    def copy(self: UF) -> UF:
        return type(self)(self.union_type, self.offset)


AnyUnionField = UnionField[UnionType]


# import cycle solution
from gd.memory.pointers import Pointer

PF = TypeVar("PF", bound="AnyPointerField")


@define()
class PointerField(Field[Pointer[T]]):
    type: Field[T] = field()
    pointer_type: Field[int] = field(factory=USize)

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

    internal_pointer_type: Type[Pointer[T]] = field(default=Pointer[T])

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

    def copy(self: PF) -> PF:
        return type(self)(self.type, self.pointer_type, self.offset, self.internal_pointer_type)


AnyPointerField = PointerField[Any]


# import cycle solution
from gd.memory.pointers import MutPointer

MPF = TypeVar("MPF", bound="AnyMutPointerField")


@define()
class MutPointerField(Field[MutPointer[T]]):
    type: Field[T] = field()
    pointer_type: Field[int] = field(factory=USize)

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

    internal_pointer_type: Type[MutPointer[T]] = field(default=MutPointer[T])

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

    def copy(self: MPF) -> MPF:
        return type(self)(self.type, self.pointer_type, self.offset, self.internal_pointer_type)


AnyMutPointerField = MutPointerField[Any]


IMMUTABLE_REFERENCE = "the reference is immutable"

R = TypeVar("R", bound="Ref")


@define()
class Ref(Field[T]):
    type: Field[T] = field()
    pointer_type: Field[int] = field(factory=USize)

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

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
        return type(self)(self.type, self.pointer_type, self.offset, self.internal_pointer_type)


AnyRef = Ref[Any]


MR = TypeVar("MR", bound="AnyMutRef")


@define()
class MutRef(Field[T]):
    type: Field[T] = field()
    pointer_type: Field[int] = field(factory=USize)

    offset: int = field(default=DEFAULT_OFFSET, repr=hex)

    internal_pointer_type: Type[MutPointer[T]] = field(default=MutPointer[T])

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
        return type(self)(self.type, self.pointer_type, self.offset, self.internal_pointer_type)


AnyMutRef = MutRef[Any]


# import cycle solution
from gd.memory.base import Base
