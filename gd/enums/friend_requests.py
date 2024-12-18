from enum import Enum

__all__ = ("FriendRequestState", "FriendRequestType")


class FriendRequestState(Enum):
    """Represents friend request states."""

    OPEN = 0
    """Friend requests are open."""

    CLOSED = 1
    """Friend requests are closed."""

    DEFAULT = OPEN
    """The default friend request state."""


class FriendRequestType(Enum):
    """Represents friend request types."""

    INCOMING = 0
    """Incoming friend requests."""

    OUTGOING = 1
    """Outgoing friend requests."""

    DEFAULT = INCOMING
    """The default friend request type."""
