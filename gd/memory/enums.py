from enum import Flag

__all__ = ("Permissions",)


class Permissions(Flag):
    """Represents permissions."""

    NONE = 0
    """No permissions."""

    EXECUTE = 1
    """Execute permissions."""

    WRITE = 2
    """Write permissions."""

    READ = 4
    """Read permissions."""

    ALL = EXECUTE | WRITE | READ
    """All permissions."""

    DEFAULT = ALL
    """Default permissions."""
