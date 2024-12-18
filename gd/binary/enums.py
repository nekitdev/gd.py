from enum import Enum

__all__ = ("ByteOrder",)


class ByteOrder(Enum):
    """Represents byte orders."""

    NATIVE = "="
    """Native byte order."""

    LITTLE = "<"
    """Little-endian byte order."""

    BIG = ">"
    """Big-endian byte order."""

    DEFAULT = NATIVE
    """Default byte order."""

    def is_native(self) -> bool:
        """Checks if the byte order is [`NATIVE`][gd.binary.enums.ByteOrder.NATIVE].

        Returns:
            Whether the byte order is [`NATIVE`][gd.binary.enums.ByteOrder.NATIVE].
        """
        return self is type(self).NATIVE

    def is_little(self) -> bool:
        """Checks if the byte order is [`LITTLE`][gd.binary.enums.ByteOrder.LITTLE].

        Returns:
            Whether the byte order is [`LITTLE`][gd.binary.enums.ByteOrder.LITTLE].
        """
        return self is type(self).LITTLE

    def is_big(self) -> bool:
        """Checks if the byte order is [`BIG`][gd.binary.enums.ByteOrder.BIG].

        Returns:
            Whether the byte order is [`BIG`][gd.binary.enums.ByteOrder.BIG].
        """
        return self is type(self).BIG

    def is_default(self) -> bool:
        """Checks if the byte order is [`DEFAULT`][gd.binary.enums.ByteOrder.DEFAULT].

        Returns:
            Whether the byte order is [`DEFAULT`][gd.binary.enums.ByteOrder.DEFAULT].
        """
        return self is type(self).DEFAULT
