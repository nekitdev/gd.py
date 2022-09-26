from abc import abstractmethod
from itertools import count
from typing import TYPE_CHECKING, Any, Iterable, Iterator, Optional, Tuple, Type, TypeVar, Union, overload
from typing_extensions import Never, Protocol

from attrs import define, field

from gd.binary_constants import (
    I8_SIZE,
    U8_SIZE,
    I16_SIZE,
    U16_SIZE,
    I32_SIZE,
    U32_SIZE,
    I64_SIZE,
    U64_SIZE,
)
from gd.enums import ByteOrder
from gd.memory.state import AbstractState
from gd.platform import PlatformConfig
from gd.typing import StringDict, is_instance

if TYPE_CHECKING:
    from gd.memory.base import Base

__all__ = ("Field", "I8", "U8", "I16", "U16", "I32", "U32", "I64", "U64", "ISize", "USize", "Size")

T = TypeVar("T")


@define()
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

    @overload
    def __get__(self: F, instance: None, type: Optional[Type[B]] = ...) -> F:
        ...

    @overload
    def __get__(self, instance: B, type: Optional[Type[B]]) -> T:
        ...

    def __get__(self: F, instance: Optional[B], type: Optional[Type[B]] = None) -> Union[F, T]:
        if instance is None:
            return self

        return self.read(instance.state, instance.address + self.offset)

    def __set__(self, instance: B, value: T) -> None:
        self.write(instance.state, instance.address + self.offset, value)

    def __delete__(self, instance: B) -> Never:
        raise AttributeError(CAN_NOT_DELETE_FIELDS)

    def copy(self: F) -> F:
        return type(self)(self.offset)


AnyField = Field[Any]


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


@define()
class Size(ISize):
    def read(self, state: AbstractState, address: int, order: ByteOrder = ByteOrder.NATIVE) -> int:
        return state.read_size(address, order)

    def write(
        self, state: AbstractState, address: int, value: int, order: ByteOrder = ByteOrder.NATIVE
    ) -> None:
        state.write_size(address, value, order)


def fetch_fields_iterator(base: Type[B]) -> Iterator[Tuple[str, AnyField]]:
    for type in reversed(base.mro()):
        for name, value in vars(type).items():
            if is_instance(value, Field):
                yield (name, value)


def fetch_fields(base: Type[B]) -> StringDict[AnyField]:
    return dict(fetch_fields_iterator(base))
