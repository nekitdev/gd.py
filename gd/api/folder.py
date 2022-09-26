from typing import BinaryIO, Type, TypeVar

from attrs import define

from gd.binary import VERSION, Binary
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.enums import ByteOrder

__all__ = ("Folder",)

F = TypeVar("F", bound="Folder")


@define()
class Folder(Binary):
    """Represents level folders."""

    id: int
    name: str

    def __hash__(self) -> int:
        return self.id

    @classmethod
    def from_binary(
        cls: Type[F],
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> F:
        reader = Reader(binary)

        id = reader.read_u8(order)

        name_length = reader.read_u8(order)

        name = reader.read(name_length).decode(encoding, errors)

        return cls(id, name)

    def to_binary(
        self,
        binary: BinaryIO,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
        encoding: str = DEFAULT_ENCODING,
        errors: str = DEFAULT_ERRORS,
    ) -> None:
        writer = Writer(binary)

        writer.write_u8(self.id, order)

        data = self.name.encode(encoding, errors)

        writer.write_u8(len(data), order)

        writer.write(data)
