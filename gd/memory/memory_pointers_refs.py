from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from gd.memory.memory import Memory, MemoryType
from gd.memory.memory_special import MemoryVoid
from gd.memory.traits import Layout, Read, ReadWrite
from gd.memory.types import uintptr
from gd.platform import SYSTEM_PLATFORM_CONFIG, PlatformConfig
from gd.typing import AnyType, DynamicTuple, Namespace

if TYPE_CHECKING:
    from gd.memory.state import AbstractState

__all__ = ("MemoryAbstractPointerType", "MemoryAbstractPointer", "MemoryPointer", "MemoryMutPointer", "MemoryRef", "MemoryMutRef")

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


PT = TypeVar("PT", bound="MemoryAbstractPointer")
PU = TypeVar("PU", bound="MemoryAbstractPointer")

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


T = TypeVar("T")


class MemoryPointer(MemoryAbstractPointer[Read[T]]):
    def __int__(self) -> int:
        return self.address

    def __bool__(self) -> bool:
        return bool(self.address)

    def __hash__(self) -> int:
        return self.address

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.state is other.state and self.address == other.address

        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.state is other.state and self.address != other.address

        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.state is other.state and self.address > other.address

        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.state is other.state and self.address < other.address

        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.state is other.state and self.address >= other.address

        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.state is other.state and self.address <= other.address

        return NotImplemented

    def get_address(self) -> int:
        return self._address

    def set_address(self, address: int) -> None:
        self._address = address

    address = class_property(get_address, set_address)

    def is_null(self) -> bool:
        return not self.value_address

    def read(self) -> T:
        address = self.value_address

        if address:
            return self.type.read_value_from(self.state, address)

        raise NullPointerError("Can not dereference null pointer.")

    value = property(read)

    def read_address(self) -> int:
        return self.pointer_type.read_value_from(self.state, self.address)

    def write_address(self, address: int) -> None:
        return self.pointer_type.write_value_to(address, self.state, self.address)

    value_address = property(read_address, write_address)

    @classmethod
    def create_from(cls: Type[PointerT], other: PointerU) -> PointerT:
        return cls(address=other.address, state=other.state)

    def copy(self: PointerT) -> PointerT:
        return self.create_from(self)

    def add_inplace(self: PointerT, value: int) -> PointerT:
        self.address += value

        return self

    __iadd__ = add_inplace

    def sub_inplace(self: PointerT, value: int) -> PointerT:
        self.address -= value

        return self

    __isub__ = sub_inplace

    def follow_inplace(self: PointerT) -> PointerT:
        self.address = self.value_address

        return self

    def offset_inplace(self: PointerT, *offsets: int) -> PointerT:
        if offsets:
            offset_iter = iter(offsets)

            self.add_inplace(next(offset_iter))

            for offset in offset_iter:
                self.follow_inplace().add_inplace(offset)

        return self

    def add(self: PointerT, value: int) -> PointerT:
        other = self.copy()

        other.add_inplace(value)

        return other

    __add__ = add

    def sub(self: PointerT, value: int) -> PointerT:
        other = self.copy()

        other.sub_inplace(value)

        return other

    __sub__ = sub

    def follow(self: PointerT) -> PointerT:
        other = self.copy()

        other.follow_inplace()

        return other

    def offset(self: PointerT, *offsets: int) -> PointerT:
        other = self.copy()

        other.offset_inplace(*offsets)

        return other

    def cast(self: PointerT, cls: Type[PointerU]) -> PointerU:
        return cls.create_from(self)


class MemoryMutPointer(MemoryPointer[T], MemoryBasePointer[ReadWriteLayout[T]]):
    _type: Type[ReadWriteLayout[T]]  # type: ignore

    @class_property
    def type(self) -> Type[ReadWriteLayout[T]]:  # type: ignore
        return self._type

    def read(self) -> T:
        return super().read()

    def write(self, value: T) -> None:
        address = self.value_address

        if address:
            return self.type.write_value_to(value, self.state, address)

        raise NullPointerError("Can not dereference null pointer.")

    value = property(read, write)


class MemoryRef(MemoryPointer[T]):
    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> T:  # type: ignore
        self = cls(state, address)

        return self.value


class MemoryMutRef(MemoryRef[T], MemoryMutPointer[T]):
    @classmethod
    def write_value_to(cls, value: T, state: "BaseState", address: int) -> None:  # type: ignore
        self = cls(state, address)

        self.value = value
