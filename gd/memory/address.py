from gd.decorators import cache_by
from gd.memory.data import Data
from gd.text_utils import make_repr
from gd.typing import TYPE_CHECKING, Any, Iterable, Tuple, Type, TypeVar, Union

if TYPE_CHECKING:
    from gd.memory.state import BaseState

AddressT = TypeVar("AddressT", bound="Address")
AddressU = TypeVar("AddressU", bound="Address")

T = TypeVar("T")


def item_to_tuple(item: Union[T, Iterable[T]]) -> Tuple[T, ...]:
    if isinstance(item, Iterable):
        return tuple(item)

    return (item,)


class Address:
    def __init__(self, address: int, state: "BaseState", signed: bool = False) -> None:
        self._address = address
        self._state = state
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
    def create_from(cls: Type[AddressT], other: AddressU) -> AddressT:
        return cls(address=other.address, state=other.state, signed=other.signed)

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

    def add_inplace(self: AddressT, value: int) -> AddressT:
        self.address += value

        return self

    __iadd__ = add_inplace

    def sub_inplace(self: AddressT, value: int) -> AddressT:
        self.address -= value

        return self

    __isub__ = sub_inplace

    def follow_inplace(self: AddressT) -> AddressT:
        self.address = self.value_address

        return self

    def offset_inplace(self: AddressT, *offsets: int) -> AddressT:
        if offsets:
            offset_iter = iter(offsets)

            self.add_inplace(next(offset_iter))

            for offset in offset_iter:
                self.follow_inplace().add_inplace(offset)

        return self

    def add(self: AddressT, value: int) -> AddressT:
        other = self.create_from(self)

        other.add_inplace(value)

        return other

    __add__ = add

    def sub(self: AddressT, value: int) -> AddressT:
        other = self.create_from(self)

        other.sub_inplace(value)

        return other

    __sub__ = sub

    def follow(self: AddressT) -> AddressT:
        other = self.create_from(self)

        other.follow_inplace()

        return other

    def offset(self: AddressT, *offsets: int) -> AddressT:
        other = self.create_from(self)

        other.offset_inplace(*offsets)

        return other

    def __getitem__(self: AddressT, offsets: Any) -> AddressT:
        return self.offset(*item_to_tuple(offsets))

    def cast(self: AddressT, cls: Type[AddressU]) -> AddressU:
        return cls.create_from(self)
