from struct import calcsize as get_size, pack, unpack

from gd.enums import ByteOrder
from gd.memory.utils import bits, class_property
from gd.typing import TYPE_CHECKING, Any, Dict, Generic, Tuple, Type, TypeVar, Union, cast

if TYPE_CHECKING:
    from gd.memory.state import BaseState

__all__ = ("Data",)

T = TypeVar("T")


class DataType(type(Generic)):  # type: ignore
    _name: str
    _format: str
    _size: int
    _alignment: int
    _order: ByteOrder

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[Any], ...],
        cls_dict: Dict[str, Any],
        name: str = "",
        format: str = "",
        alignment: int = 0,
        **kwargs,
    ) -> "DataType":
        cls = super().__new__(meta_cls, cls_name, bases, cls_dict, **kwargs)

        size = get_size(format)

        cls._name = name
        cls._format = format
        cls._size = size
        cls._alignment = alignment or size

        return cls  # type: ignore

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
    def alignment(cls) -> int:
        return cls._alignment

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
    _alignment: int = 0
    _order: ByteOrder = ByteOrder.NATIVE  # type: ignore

    def __init__(self, value: T) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def get_value(self) -> T:
        return self._value

    def set_value(self, value: T) -> None:
        self._value = value

    value = property(get_value, set_value)

    @class_property
    def name(self) -> str:
        return self._name

    @class_property
    def format(self) -> str:
        return self._format

    @class_property
    def size(self) -> int:
        return self._size

    @class_property
    def alignment(self) -> int:
        return self._alignment

    @class_property
    def bits(self) -> int:
        return bits(self.size)

    def get_order(self) -> ByteOrder:
        return self._order

    def set_order(self, order: Union[str, ByteOrder]) -> None:
        self._order = ByteOrder.from_value(order)

    order = property(get_order, set_order)

    @property
    def pack_format(self) -> str:
        return self.order.value + self.format

    @classmethod
    def read_from(cls: Type["Data[T]"], state: "BaseState", address: int) -> "Data[T]":
        return cls(cls.read_value_from(state, address))

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> T:
        result = unpack(cast(str, cls.pack_format), state.read_at(address, cast(int, cls.size)))

        if len(result) == 1:
            (result,) = result

        return cast(T, result)

    def write_to(self, state: "BaseState", address: int) -> None:
        self.write_value_to(self.value, state, address)

    @classmethod
    def write_value_to(cls, value: T, state: "BaseState", address: int) -> None:
        state.write_at(address, pack(cast(str, cls.pack_format), value))
