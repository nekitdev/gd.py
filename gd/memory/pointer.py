from gd.memory.address import Address
from gd.memory.object import Object
from gd.typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar

PointerT = TypeVar("PointerT", bound="Pointer")
T = TypeVar("T")

if TYPE_CHECKING:
    from gd.memory.state import BaseState


class Pointer(Generic[T], Address):
    def __init__(
        self,
        address: int,
        state: "BaseState",
        signed: bool = False,
        type: Optional[Type[Object[T]]] = None,
    ) -> None:
        super().__init__(address, state, signed=signed)

        self.type_unchecked = type

    def add(self: PointerT, value: int) -> PointerT:
        return self.__class__(self.address + value, self.state, self.signed, self.type_unchecked)

    def sub(self: PointerT, value: int) -> PointerT:
        return self.__class__(self.address - value, self.state, self.signed, self.type_unchecked)

    def follow(self: PointerT) -> PointerT:
        return self.__class__(self.value_address, self.state, self.signed, self.type_unchecked)

    def with_type(self: PointerT, type: Type[Object[T]]) -> PointerT:
        self.type = type

        return self

    def get_type(self) -> Type[Object[T]]:
        type_unchecked = self.type_unchecked

        if type_unchecked is None:
            raise ValueError("Pointer type is not set.")

        return type_unchecked

    def set_type(self, type: Optional[Type[Object[T]]]) -> None:
        self.type_unchecked = type

    def delete_type(self) -> None:
        self.type_unchecked = None

    type = property(get_type, set_type, delete_type)

    def get_value(self) -> T:
        return self.state.read(self.type, self.value_address)

    def set_value(self, value: T) -> None:
        self.state.write(self.type, value, self.value_address)

    value = property(get_value, set_value)

    def get_object(self) -> Object[T]:
        return self.state.read_object(self.type, self.value_address)

    def set_object(self, object: Object[T]) -> None:
        self.state.write_object(self.type, self.value_address)

    object = property(get_object, set_object)
