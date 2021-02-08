from struct import calcsize as get_size, pack, unpack

from gd.enums import ByteOrder
from gd.memory.utils import bits
from gd.typing import TYPE_CHECKING, Generic, Type, TypeVar, Union, cast

if TYPE_CHECKING:
    from gd.memory.state import BaseState

__all__ = ("Data",)

T = TypeVar("T")


class DataType(type(Generic)):  # type: ignore
    _name: str
    _format: str
    _size: int
    _order: ByteOrder

    @property
    def name(cls) -> str:
        return cls._name

    @property
    def format(cls) -> str:
        return cls._format

    @property
    def size(cls) -> int:
        return cls._size

    @property
    def bits(cls) -> int:
        return bits(cls.size)

    def get_order(cls) -> ByteOrder:
        return cls._order

    def set_order(cls, order: Union[str, ByteOrder]) -> None:
        cls._order = ByteOrder.from_value(order)

    order = property(get_order, set_order)

    @property
    def pack_format(cls) -> str:
        return cls.order.value + cls.format


class Data(Generic[T], metaclass=DataType):
    _name: str = ""
    _format: str = ""
    _size: int = 0
    _order: ByteOrder = ByteOrder.NATIVE  # type: ignore

    def __init_subclass__(cls, name: str, format: str) -> None:
        cls._name = name
        cls._format = format
        cls._size = get_size(format)

    def __init__(self, value: T) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def get_value(self) -> T:
        return self._value

    def set_value(self, value: T) -> None:
        self._value = value

    value = property(get_value, set_value)

    @property
    def name(self) -> str:
        return cast(str, self.__class__.name)

    @property
    def format(self) -> str:
        return cast(str, self.__class__.format)

    @property
    def size(self) -> int:
        return cast(int, self.__class__.size)

    @property
    def bits(self) -> int:
        return bits(self.size)

    def get_order(cls) -> ByteOrder:
        return cls._order

    def set_order(cls, order: Union[str, ByteOrder]) -> None:
        cls._order = ByteOrder.from_value(order)

    order = property(get_order, set_order)

    @property
    def pack_format(self) -> str:
        return self.order.value + self.format

    @classmethod
    def read(cls: Type["Data[T]"], state: "BaseState", address: int) -> "Data[T]":
        return cls(cls.read_value(state, address))

    @classmethod
    def read_value(cls, state: "BaseState", address: int) -> T:
        result = unpack(cast(str, cls.pack_format), state.read_at(address, cast(int, cls.size)))

        if len(result) == 1:
            (result,) = result

        return cast(T, result)

    def write(self, state: "BaseState", address: int) -> None:
        self.write_value(self.value, state, address)

    @classmethod
    def write_value(cls, value: T, state: "BaseState", address: int) -> None:
        state.write_at(address, pack(cast(str, cls.pack_format), value))
