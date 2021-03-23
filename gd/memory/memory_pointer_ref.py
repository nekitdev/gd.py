# DOCUMENT

from gd.memory.memory import MemoryType, Memory
from gd.memory.traits import Layout, ReadLayout, ReadWriteLayout
from gd.memory.utils import class_property
from gd.platform import Platform, system_bits, system_platform
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Tuple, Type, TypeVar, Union

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("MemoryPointer", "MemoryMutPointer", "MemoryRef", "MemoryMutRef")

L = TypeVar("L", bound=Layout)
T = TypeVar("T")


class NullPointerError(RuntimeError):
    pass


class MemoryPointerType(MemoryType):
    _type: Type[Layout]
    _pointer_type: Type[ReadWriteLayout[int]]

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        type: Optional[Type[Layout]] = None,
        pointer_type: Optional[Type[ReadWriteLayout[int]]] = None,
        bits: int = system_bits,
        platform: Union[int, str, Platform] = system_platform,
        **kwargs,
    ) -> "MemoryPointerType":
        cls = super().__new__(
            meta_cls, cls_name, bases, cls_dict, bits=bits, platform=platform, **kwargs
        )

        if type is not None:
            cls._type = type  # type: ignore

        if pointer_type is not None:
            cls._pointer_type = pointer_type  # type: ignore

        return cls  # type: ignore

    @property
    def pointer_type(cls) -> Type[ReadWriteLayout[int]]:
        return cls._pointer_type

    @property
    def type(cls) -> Type[Layout]:
        return cls._type

    @property
    def size(cls) -> int:
        return cls.pointer_type.size

    @property
    def alignment(cls) -> int:
        return cls.pointer_type.alignment


PointerT = TypeVar("PointerT", bound="MemoryPointer")
PointerU = TypeVar("PointerU", bound="MemoryPointer")


class MemoryBasePointer(Generic[L], Memory, metaclass=MemoryPointerType):
    _type: Type[L]
    _pointer_type: Type[ReadWriteLayout[int]]

    @class_property
    def pointer_type(self) -> Type[ReadWriteLayout[int]]:
        return self._pointer_type

    @class_property
    def type(self) -> Type[L]:
        return self._type

    @class_property
    def size(self) -> int:
        return self.pointer_type.size

    @class_property
    def alignment(self) -> int:
        return self.pointer_type.alignment

    def write_to(self, state: "BaseState", address: int) -> None:
        ...


class MemoryPointer(MemoryBasePointer[ReadLayout[T]]):
    _type: Type[ReadLayout[T]]

    @class_property
    def type(self) -> Type[ReadLayout[T]]:  # type: ignore
        return self._type

    def __repr__(self) -> str:
        info = {"type": self.type, "pointer_type": self.pointer_type}

        return make_repr(self, info)

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
