from io import BufferedReader, BufferedWriter
from typing import Any, Protocol, runtime_checkable

from typing_aliases import is_instance, required
from typing_extensions import Self, TypeGuard

__all__ = (
    # protocols
    "FromBinary",
    "ToBinary",
    "Binary",
    # type guards
    "is_from_binary",
    "is_to_binary",
)


@runtime_checkable
class FromBinary(Protocol):
    """Represents types that can be created from binary data."""

    @classmethod
    @required
    def from_binary(cls, binary: BufferedReader) -> Self:
        """Reads an instance from the given binary stream.

        Arguments:
            binary: The binary stream to read from.

        Returns:
            The instance read from the stream.
        """
        ...

    @classmethod
    @required
    def from_binary_packed(cls, binary: BufferedReader) -> Self:
        """Reads an instance from the given packed binary stream.

        Arguments:
            binary: The packed binary stream to read from.

        Returns:
            The instance read from the packed stream.
        """
        ...

    @classmethod
    @required
    def from_bytes(cls, data: bytes) -> Self:
        """Creates an instance from the given binary data.

        Arguments:
            data: The binary data to create an instance from.

        Returns:
            The instance created from the data.
        """
        ...

    @classmethod
    @required
    def from_bytes_packed(cls, data: bytes) -> Self:
        """Creates an instance from the given packed binary data.

        Arguments:
            data: The packed binary data to create an instance from.

        Returns:
            The instance created from the packed data.
        """
        ...


def is_from_binary(item: Any) -> TypeGuard[FromBinary]:
    """Checks if the given item is [`FromBinary`][gd.binary.protocols.FromBinary].

    Returns:
        Whether the item is [`FromBinary`][gd.binary.protocols.FromBinary].
    """
    return is_instance(item, FromBinary)


@runtime_checkable
class ToBinary(Protocol):
    """Represents types that can be converted to binary data."""

    @required
    def to_binary(self, binary: BufferedWriter) -> None:
        """Writes the instance to the given binary stream.

        Arguments:
            binary: The binary stream to write to.
        """
        ...

    @required
    def to_binary_packed(self, binary: BufferedWriter) -> None:
        """Writes the instance to the given packed binary stream.

        Arguments:
            binary: The packed binary stream to write to.
        """
        ...

    @required
    def to_bytes(self) -> bytes:
        """Converts the instance to binary data.

        Returns:
            The binary data created from the instance.
        """
        ...

    @required
    def to_bytes_packed(self) -> bytes:
        """Converts the instance to packed binary data.

        Returns:
            The packed binary data created from the instance.
        """
        ...


def is_to_binary(item: Any) -> TypeGuard[ToBinary]:
    """Checks if the given item is [`ToBinary`][gd.binary.protocols.ToBinary].

    Returns:
        Whether the item is [`ToBinary`][gd.binary.protocols.ToBinary].
    """
    return is_instance(item, ToBinary)


@runtime_checkable
class Binary(FromBinary, ToBinary, Protocol):
    """Represents types that implement both [`FromBinary`][gd.binary.protocols.FromBinary]
    and [`ToBinary`][gd.binary.protocols.ToBinary] protocols.
    """
