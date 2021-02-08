from gd.decorators import cache_by
from gd.iter_utils import item_to_tuple
from gd.memory.data import Data
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Any, Type, TypeVar

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("Pointer",)

PointerT = TypeVar("PointerT", bound="Pointer")
PointerU = TypeVar("PointerU", bound="Pointer")


class Pointer:
    def __init__(self, state: "BaseState", address: int, signed: bool = False) -> None:
        self._state = state
        self._address = address
        self._signed = signed

    def __repr__(self) -> str:
        info = {"address": hex(self.address), "signed": self.signed}

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

    @classmethod
    def create_from(cls: Type[PointerT], other: PointerU) -> PointerT:
        return cls(address=other.address, state=other.state, signed=other.signed)

    def copy(self: PointerT) -> PointerT:
        return self.create_from(self)

    @property  # type: ignore
    @cache_by("signed")
    def pointer_type(self) -> Type[Data[int]]:
        types = self.state.types
        return types.intptr_t if self.signed else types.uintptr_t

    def get_address(self) -> int:
        return self._address

    def set_address(self, address: int) -> None:
        self._address = address

    address = property(get_address, set_address)

    def get_state(self) -> "BaseState":
        return self._state

    def set_state(self, state: "BaseState") -> None:
        self._state = state

    state = property(get_state, set_state)

    def get_signed(self) -> bool:
        return self._signed

    def set_signed(self, signed: bool) -> None:
        self._signed = signed

    signed = property(get_signed, set_signed)

    @property  # type: ignore
    @cache_by("address")
    def value_address(self) -> int:
        return self.state.read(self.pointer_type, self.address)

    @classmethod
    def read(cls: Type[PointerT], state: "BaseState", address: int) -> PointerT:
        return cls.read_value(state, address)

    @classmethod
    def read_value(cls: Type[PointerT], state: "BaseState", address: int) -> PointerT:
        return cls(state, address)

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

    def __getitem__(self: PointerT, offsets: Any) -> PointerT:
        return self.offset(*item_to_tuple(offsets))

    def cast(self: PointerT, cls: Type[PointerU]) -> PointerU:
        return cls.create_from(self)
