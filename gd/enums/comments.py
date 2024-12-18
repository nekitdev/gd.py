from enum import Enum

__all__ = ("CommentState", "CommentType")


class CommentState(Enum):
    """Represents comment states."""

    OPEN_TO_ALL = 0
    """Comments are open to everyone."""

    OPEN_TO_FRIENDS = 1
    """Comments are open to friends only."""

    CLOSED = 2
    """Comments are closed."""

    DEFAULT = OPEN_TO_ALL
    """The default comment state."""


class CommentType(Enum):
    """Represents comment types."""

    USER = 0
    """User comments."""

    LEVEL = 1
    """Level comments."""
