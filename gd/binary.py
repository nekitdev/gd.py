from abc import abstractmethod
from io import BytesIO
from typing import Any, Optional, Type, TypeVar

from typing_extensions import Protocol, TypeGuard, runtime_checkable

from gd.enums import ByteOrder
from gd.typing import is_instance

__all__ = (
    "BinaryReader", "BinaryWriter", "Binary", "FromBinary", "ToBinary", "is_from_binary", "is_to_binary"
)

HEADER = b"GD"
VERSION = 1

B = TypeVar("B", bound="FromBinary")


class BinaryReader(Protocol):
    @abstractmethod
    def read(self, __size: int) -> bytes:
        ...


class BinaryWriter(Protocol):
    @abstractmethod
    def write(self, __data: bytes) -> Optional[int]:
        ...


@runtime_checkable
class FromBinary(Protocol):
    @classmethod
    @abstractmethod
    def from_binary(
        cls: Type[B],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> B:
        ...

    @classmethod
    def from_bytes(
        cls: Type[B], data: bytes, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> B:
        return cls.from_binary(BytesIO(data), order, version)


def is_from_binary(item: Any) -> TypeGuard[FromBinary]:
    return is_instance(item, FromBinary)


@runtime_checkable
class ToBinary(Protocol):
    @abstractmethod
    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> None:
        ...

    def to_bytes(self, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION) -> bytes:
        buffer = BytesIO()

        self.to_binary(buffer, order, version)

        buffer.seek(0)

        return buffer.read()


def is_to_binary(item: Any) -> TypeGuard[ToBinary]:
    return is_instance(item, ToBinary)


@runtime_checkable
class Binary(FromBinary, ToBinary, Protocol):
    pass
