from enum import Enum

__all__ = ("Length", "Privacy")


class Length(Enum):
    """Represents level lengths."""

    TINY = 0
    """*Tiny* level length."""

    SHORT = 1
    """*Short* level length."""

    MEDIUM = 2
    """*Medium* level length."""

    LONG = 3
    """*Long* level length."""

    XL = 4
    """*XL* level length."""

    PLATFORMER = 5
    """*Platformer* level length."""

    DEFAULT = TINY
    """The default level length."""

    def is_platformer(self) -> bool:
        """Checks if the level length is [`PLATFORMER`][gd.enums.levels.Length.PLATFORMER].

        Returns:
            Whether the level length is [`PLATFORMER`][gd.enums.levels.Length.PLATFORMER].
        """
        return self is type(self).PLATFORMER

    def is_default(self) -> bool:
        """Checks if the level length is [`DEFAULT`][gd.enums.levels.Length.DEFAULT].

        Returns:
            Whether the level length is [`DEFAULT`][gd.enums.levels.Length.DEFAULT].
        """
        return self is type(self).DEFAULT


class Privacy(Enum):
    """Represents level privacy."""

    PUBLIC = 0
    """Public levels."""

    FRIENDS = 1
    """Friends-only levels."""

    PRIVATE = 2
    """Private levels."""

    DEFAULT = PUBLIC
    """The default level privacy."""

    def is_private(self) -> bool:
        """Checks if the level privacy is [`PRIVATE`][gd.enums.levels.Privacy.PRIVATE].

        Returns:
            Whether the level privacy is [`PRIVATE`][gd.enums.levels.Privacy.PRIVATE].
        """
        return self is type(self).PRIVATE

    def is_friends(self) -> bool:
        """Checks if the level privacy is [`FRIENDS`][gd.enums.levels.Privacy.FRIENDS].

        Returns:
            Whether the level privacy is [`FRIENDS`][gd.enums.levels.Privacy.FRIENDS].
        """
        return self is type(self).FRIENDS

    def is_public(self) -> bool:
        """Checks if the level privacy is [`PUBLIC`][gd.enums.levels.Privacy.PUBLIC].

        Returns:
            Whether the level privacy is [`PUBLIC`][gd.enums.levels.Privacy.PUBLIC].
        """
        return self is type(self).PUBLIC

    def is_default(self) -> bool:
        """Checks if the level privacy is [`DEFAULT`][gd.enums.levels.Privacy.DEFAULT].

        Returns:
            Whether the level privacy is [`DEFAULT`][gd.enums.levels.Privacy.DEFAULT].
        """
        return self is type(self).DEFAULT
