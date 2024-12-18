from enum import Enum

__all__ = ("MessageState", "MessageType")


class MessageState(Enum):
    """Represents message states."""

    OPEN_TO_ALL = 0
    """Messages are open to everyone."""

    OPEN_TO_FRIENDS = 1
    """Messages are open to friends only."""

    CLOSED = 2
    """Messages are closed."""

    DEFAULT = OPEN_TO_ALL
    """The default message state."""


class MessageType(Enum):
    INCOMING = 0
    """Incoming messages."""

    OUTGOING = 1
    """Outgoing messages."""

    DEFAULT = INCOMING
    """The default message type."""
