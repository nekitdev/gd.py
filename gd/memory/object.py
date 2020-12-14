from gd.decorators import classproperty
from gd.enums import ByteOrder
from gd.typing import Protocol, Type, TypeVar, Union

__all__ = ("Object",)

ObjectT = TypeVar("ObjectT", bound="Object")
T = TypeVar("T")

BYTE_BITS = 8


class Object(Protocol[T]):
    @classproperty
    def size(cls) -> int:
        raise NotImplementedError("Derived classes should implement size class property.")

    @classproperty
    def bits(cls) -> int:
        return cls.size * BYTE_BITS  # type: ignore

    @classmethod
    def from_bytes(
        cls: Type[ObjectT], data: bytes, byte_order: Union[str, ByteOrder] = ByteOrder.NATIVE
    ) -> ObjectT:
        raise NotImplementedError(
            "Derived classes should implement from_bytes(data, byte_order?) class method."
        )

    def to_bytes(self: ObjectT, byte_order: Union[str, ByteOrder] = ByteOrder.NATIVE) -> bytes:
        raise NotImplementedError("Derived classes should implement to_bytes(byte_order?) method.")

    @classmethod
    def value_to_bytes(
        cls: Type[ObjectT], value: T, byte_order: Union[str, ByteOrder] = ByteOrder.NATIVE
    ) -> bytes:
        raise NotImplementedError(
            "Derived classes should implement value_to_bytes(value, byte_order?) method."
        )

    @classmethod
    def value_from_bytes(
        cls: Type[ObjectT], data: bytes, byte_order: Union[str, ByteOrder] = ByteOrder.NATIVE
    ) -> T:
        raise NotImplementedError(
            "Derived classes should implement value_from_bytes(data, byte_order?) method."
        )
