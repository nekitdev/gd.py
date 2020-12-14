from gd.decorators import cache_by
from gd.memory.data import Data
from gd.typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from gd.memory.state import BaseState

AddressT = TypeVar("AddressT", bound="Address")
AddressU = TypeVar("AddressU", bound="Address")


class Address:
    def __init__(self, address: int, state: "BaseState", signed: bool = False) -> None:
        self._address = address
        self._state = state
        self._signed = signed

    @property  # type: ignore
    @cache_by("signed")
    def pointer_type(self) -> Type[Data[int]]:
        types = self.state.types
        return types.intptr_t if self.signed else types.uintptr_t

    @property
    def address(self) -> int:
        return self._address

    @property
    def state(self) -> "BaseState":
        return self._state

    @property
    def signed(self) -> bool:
        return self._signed

    @property  # type: ignore
    @cache_by("address")
    def value_address(self) -> int:
        return self.state.read(self.pointer_type, self.address)

    def add(self: AddressT, value: int) -> AddressT:
        return self.__class__(self.address + value, self.state, self.signed)

    def sub(self: AddressT, value: int) -> AddressT:
        return self.__class__(self.address - value, self.state, self.signed)

    def follow(self: AddressT) -> AddressT:
        return self.__class__(self.value_address, self.state, self.signed)

    def offset(self: AddressT, *offsets: int) -> AddressT:
        address = self

        if offsets:
            offset_iter = iter(offsets)

            address = address.add(next(offset_iter))

            for offset in offset_iter:
                address = address.follow().add(offset)

        return address

    def cast(self: AddressT, cls: Type[AddressU], *args, **kwargs) -> AddressU:
        return cls(self.address, self.state, *args, **kwargs)
