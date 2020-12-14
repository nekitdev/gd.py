from struct import calcsize, pack, unpack

from gd.decorators import classproperty
from gd.enums import ByteOrder
from gd.memory.object import Object
from gd.typing import Callable, Type, TypeVar, Union, cast

__all__ = ("Data", "data")

T = TypeVar("T")

BYTE_BITS = 8


class Data(Object[T]):
    _name: str = ""
    _format: str = ""
    _size: int = 0

    @classproperty
    def name(cls) -> str:
        return cls._name

    @classproperty
    def format(cls) -> str:
        return cls._format

    @classproperty
    def size(cls) -> int:
        return cls._size

    @classproperty
    def bits(cls) -> int:
        return cls._size * BYTE_BITS

    @classmethod
    def create_format(cls, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> str:
        return ByteOrder.from_value(order).value + cls.format

    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{self.name}({self.value!r})"

    @classmethod
    def from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> "Data[T]":
        return cls(cls.value_from_bytes(data, order))

    def to_bytes(self, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return self.value_to_bytes(self.value, order)

    @classmethod
    def value_from_bytes(cls, data: bytes, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> T:
        result = unpack(cls.create_format(order), data)

        if len(result) == 1:
            (result,) = result

        return cast(T, result)

    @classmethod
    def value_to_bytes(cls, value: T, order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        return pack(cls.create_format(order), value)

    @property
    def value(self) -> T:
        return self._value

    @property
    def type(self) -> Type["Data[T]"]:
        return type(self)


def data(name: str, format: str = "") -> Callable[[Type[Data[T]]], Type[Data[T]]]:
    def decorator(cls: Type[Data[T]]) -> Type[Data[T]]:
        cls._name = name
        cls._format = format
        cls._size = calcsize(format)

        return cls

    return decorator
