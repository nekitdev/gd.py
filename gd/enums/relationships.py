from enum import Enum

__all__ = ("RelationshipState", "RelationshipType")


class RelationshipState(Enum):
    """Represents relationship states."""

    NONE = 0
    """No relationships."""

    FRIENDS = 1
    """Friends."""

    BLOCKED = 2
    """Blocked."""

    OUTGOING_REQUEST = 3
    """Outgoing request."""

    INCOMING_REQUEST = 4
    """Incoming request."""

    DEFAULT = NONE
    """The default relationship state."""


class RelationshipType(Enum):
    """Represents relationship types."""

    FRIENDS = 0
    """Friends."""

    BLOCKED = 1
    """Blocked."""
