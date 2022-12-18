from __future__ import annotations

from abc import abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any, Optional, Type, TypeVar

from attrs import frozen
from typing_extensions import Protocol, TypeGuard, runtime_checkable

from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.encoding import compress, decompress
from gd.enums import ByteOrder
from gd.typing import IntoPath, is_instance

__all__ = (
    "VERSION",
    "BinaryReader",
    "BinaryWriter",
    "Binary",
    "FromBinary",
    "ToBinary",
    "is_from_binary",
    "is_to_binary",
    "dump",
    "dump_to",
    "dump_bytes",
    "load",
    "load_from",
    "load_bytes",
)

VERSION = 1

B = TypeVar("B", bound="FromBinary")

DEFAULT_SIZE = -1


class BinaryReader(Protocol):
    @abstractmethod
    def read(self, __size: int = DEFAULT_SIZE) -> bytes:
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
    def from_binary_with_info(cls: Type[B], binary: BinaryReader, info: BinaryInfo) -> B:
        return cls.from_binary(binary, info.order, info.version)

    @classmethod
    def from_bytes(
        cls: Type[B], data: bytes, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> B:
        return cls.from_binary(BytesIO(data), order, version)

    @classmethod
    def from_bytes_with_info(cls: Type[B], data: bytes, info: BinaryInfo) -> B:
        return cls.from_bytes(data, info.order, info.version)


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

    def to_binary_with_info(self, binary: BinaryWriter, info: BinaryInfo) -> None:
        self.to_binary(binary, info.order, info.version)

    def to_bytes(self, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION) -> bytes:
        buffer = BytesIO()

        self.to_binary(buffer, order, version)

        buffer.seek(0)

        return buffer.read()

    def to_bytes_with_info(self, info: BinaryInfo) -> bytes:
        return self.to_bytes(info.order, info.version)


def is_to_binary(item: Any) -> TypeGuard[ToBinary]:
    return is_instance(item, ToBinary)


@runtime_checkable
class Binary(FromBinary, ToBinary, Protocol):
    pass


BI = TypeVar("BI", bound="BinaryInfo")

INVALID_HEADER = "invalid header; expected {}"

HEADER = b"GD"

HEADER_SIZE = len(HEADER)
BYTE_ORDER_SIZE = 1


@frozen()
class BinaryInfo(Binary):
    version: int = VERSION
    order: ByteOrder = ByteOrder.DEFAULT

    @classmethod
    def from_binary(
        cls: Type[BI],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> BI:
        reader = Reader(binary)

        header = reader.read(HEADER_SIZE)

        expected = HEADER

        if header != expected:
            raise ValueError(INVALID_HEADER.format(expected))

        version = reader.read_u8(order)

        order = ByteOrder(reader.read(BYTE_ORDER_SIZE).decode(encoding, errors))

        return cls(version, order)

    def to_binary(
        self,
        binary: BinaryWriter,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary)

        writer.write(HEADER)

        writer.write_u8(self.version, order)

        writer.write(self.order.value.encode(encoding, errors))


READ_BINARY = "rb"
WRITE_BINARY = "wb"


def dump(binary: BinaryWriter, item: ToBinary, info: Optional[BinaryInfo] = None) -> None:
    binary.write(dump_bytes(item, info))


def dump_to(path: IntoPath, item: ToBinary, info: Optional[BinaryInfo] = None) -> None:
    with Path(path).open(WRITE_BINARY) as file:
        dump(file, item, info)


def dump_bytes(item: ToBinary, info: Optional[BinaryInfo] = None) -> bytes:
    if info is None:
        info = BinaryInfo()

    return compress(info.to_bytes() + item.to_bytes_with_info(info))


def load(binary: BinaryReader, type: Type[B], info_type: Type[BinaryInfo] = BinaryInfo) -> B:
    return load_bytes(binary.read(), type, info_type)


def load_from(path: IntoPath, type: Type[B], info_type: Type[BinaryInfo] = BinaryInfo) -> B:
    with Path(path).open(READ_BINARY) as file:
        return load(file, type, info_type)


def load_bytes(data: bytes, type: Type[B], info_type: Type[BinaryInfo] = BinaryInfo) -> B:
    binary = BytesIO(decompress(data))

    info = info_type.from_binary(binary)

    item = type.from_binary_with_info(binary, info)

    return item


from gd.binary_utils import Reader, Writer  # noqa
