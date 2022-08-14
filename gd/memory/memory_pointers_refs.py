from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from gd.errors import NullPointerError
from gd.memory.memory import Memory, MemoryType
from gd.memory.memory_special import MemoryVoid
from gd.memory.traits import Layout, Read, ReadWrite
from gd.memory.types import uintptr
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace, is_same_type

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = (
    "MemoryAbstractPointerType",
    "MemoryAbstractPointer",
    "MemoryPointer",
    "MemoryMutPointer",
    "MemoryRef",
    "MemoryMutRef",
)

MAPT = TypeVar("MAPT", bound="MemoryAbstractPointerType")


class MemoryAbstractPointerType(MemoryType):
    _type: Type[Layout]
    _pointer_type: Type[ReadWrite[int]]

    def __new__(
        cls: Type[MAPT],
        name: str,
        bases: DynamicTuple[AnyType],
        namespace: Namespace,
        type: Type[Layout] = MemoryVoid,
        pointer_type: Type[ReadWrite[int]] = uintptr,
        config: PlatformConfig = SYSTEM_PLATFORM_CONFIG,
        **keywords: Any,
    ) -> MAPT:
        self = super().__new__(cls, name, bases, namespace, config=config)

        self._type = type

        self._pointer_type = pointer_type

        return self

    @property
    def pointer_type(self) -> Type[ReadWrite[int]]:
        return self._pointer_type

    @property
    def type(self) -> Type[Layout]:
        return self._type

    @property
    def size(self) -> int:
        return self.pointer_type.size

    @property
    def alignment(self) -> int:
        return self.pointer_type.alignment


L = TypeVar("L", bound=Layout)


class MemoryAbstractPointer(Generic[L], Memory, metaclass=MemoryAbstractPointerType):
    _type: Type[L]
    _pointer_type: Type[ReadWrite[int]]

    @property
    def pointer_type(self) -> Type[ReadWrite[int]]:
        return self._pointer_type

    @property
    def type(self) -> Type[L]:
        return self._type


PT = TypeVar("PT", bound="AnyMemoryPointer")
PU = TypeVar("PU", bound="AnyMemoryPointer")

T = TypeVar("T")


class MemoryPointer(MemoryAbstractPointer[Read[T]]):
    def __int__(self) -> int:
        return self.address

    def __bool__(self) -> bool:
        return bool(self.address)

    def __hash__(self) -> int:
        return self.address

    def __eq__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return self.state is other.state and self.address == other.address

        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return self.state is other.state and self.address != other.address

        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return self.state is other.state and self.address > other.address

        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return self.state is other.state and self.address < other.address

        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return self.state is other.state and self.address >= other.address

        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if is_same_type(other, self):
            return self.state is other.state and self.address <= other.address

        return NotImplemented

    def is_null(self) -> bool:
        return not self.value_address

    def read(self) -> T:
        address = self.value_address

        if address:
            return self.type.read_value_from(self.state, address)

        raise NullPointerError()

    value = property(read)

    def read_address(self) -> int:
        return self.pointer_type.read_value_from(self.state, self.address)

    def write_address(self, address: int) -> None:
        return self.pointer_type.write_value_to(self.state, address, self.address)

    value_address = property(read_address, write_address)

    @classmethod
    def create_from(cls: Type[PT], other: PU) -> PT:
        return cls(address=other.address, state=other.state)

    def copy(self: PT) -> PT:
        return self.create_from(self)

    def add_in_place(self: PT, value: int) -> PT:
        self.address += value

        return self

    __iadd__ = add_in_place

    def sub_in_place(self: PT, value: int) -> PT:
        self.address -= value

        return self

    __isub__ = sub_in_place

    def follow_in_place(self: PT) -> PT:
        self.address = self.value_address

        return self

    def offset_in_place(self: PT, *offsets: int) -> PT:
        if offsets:
            iterator = iter(offsets)

            self.add_in_place(next(iterator))

            for offset in iterator:
                self.follow_in_place().add_in_place(offset)

        return self

    def add(self: PT, value: int) -> PT:
        copy = self.copy()

        copy.add_in_place(value)

        return copy

    __add__ = add

    def sub(self: PT, value: int) -> PT:
        copy = self.copy()

        copy.sub_in_place(value)

        return copy

    __sub__ = sub

    def follow(self: PT) -> PT:
        copy = self.copy()

        copy.follow_in_place()

        return copy

    def offset(self: PT, *offsets: int) -> PT:
        copy = self.copy()

        copy.offset_in_place(*offsets)

        return copy

    def cast(self: PT, type: Type[PU]) -> PU:
        return type.create_from(self)


AnyMemoryPointer = MemoryPointer[Any]


class MemoryMutPointer(MemoryPointer[T], MemoryAbstractPointer[ReadWrite[T]]):
    def read(self) -> T:
        return super().read()

    def write(self, value: T) -> None:
        address = self.value_address

        if address:
            return self.type.write_value_to(self.state, value, address)

        raise NullPointerError()

    value = property(read, write)


class MemoryRef(MemoryPointer[T]):
    @classmethod
    def read_value_from(cls, state: AbstractState, address: int) -> T:  # type: ignore
        self = cls(state, address)

        return self.value


class MemoryMutRef(MemoryRef[T], MemoryMutPointer[T]):
    @classmethod
    def write_value_to(cls, state: AbstractState, value: T, address: int) -> None:  # type: ignore
        self = cls(state, address)

        self.value = value
