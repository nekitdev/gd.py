from typing import Type, TypeVar

from attrs import define

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.enums import ByteOrder

__all__ = ("Folder",)

F = TypeVar("F", bound="Folder")


@define()
class Folder(Binary):
    """Represents level folders.

    Binary:
        ```text
        struct Folder {
            id: u8,
            name_length: u8,
            name: [u8; name_length],
        }
        ```
    """

    id: int
    """The ID of the folder."""
    name: str
    """The name of the folder."""

    def __hash__(self) -> int:
        return self.id

    @classmethod
    def from_binary(
        cls: Type[F],
        binary: BinaryReader,
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
        binary: BinaryWriter,
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
