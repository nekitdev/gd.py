from enum import Enum

__all__ = ("Role",)


class Role(Enum):
    """Represents roles."""

    REGULAR = 0
    """Regular."""

    MODERATOR = 1
    """Moderator."""

    ELDER_MODERATOR = 2
    """Elder moderator."""

    DEFAULT = REGULAR
    """The default role."""

    def is_regular(self) -> bool:
        """Checks if the role is [`REGULAR`][gd.enums.roles.Role.REGULAR].

        Returns:
            Whether the role is [`REGULAR`][gd.enums.roles.Role.REGULAR].
        """
        return self is type(self).REGULAR

    def is_moderator(self) -> bool:
        """Checks if the role is [`MODERATOR`][gd.enums.roles.Role.MODERATOR].

        Returns:
            Whether the role is [`MODERATOR`][gd.enums.roles.Role.MODERATOR].
        """
        return self is type(self).MODERATOR

    def is_elder_moderator(self) -> bool:
        """Checks if the role is [`ELDER_MODERATOR`][gd.enums.roles.Role.ELDER_MODERATOR].

        Returns:
            Whether the role is [`ELDER_MODERATOR`][gd.enums.roles.Role.ELDER_MODERATOR].
        """
        return self is type(self).ELDER_MODERATOR

    def is_default(self) -> bool:
        """Checks if the role is [`DEFAULT`][gd.enums.roles.Role.DEFAULT].

        Returns:
            Whether the role is [`DEFAULT`][gd.enums.roles.Role.DEFAULT].
        """
        return self is type(self).DEFAULT
