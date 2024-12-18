from typing import Any, Protocol, runtime_checkable

from typing_aliases import is_instance, required
from typing_extensions import Self, TypeGuard

__all__ = (
    # protocols
    "FromRobTop",
    "ToRobTop",
    "RobTop",
    # type guards
    "is_from_robtop",
    "is_to_robtop",
)


@runtime_checkable
class FromRobTop(Protocol):
    """Represents types that can be parsed from RobTop's format."""

    @classmethod
    @required
    def from_robtop(cls, string: str) -> Self:
        ...

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return False


def is_from_robtop(item: Any) -> TypeGuard[FromRobTop]:
    """Checks if the given item is [`FromRobTop`][gd.internals.robtop.protocols.FromRobTop].

    Arguments:
        item: The item to check.

    Returns:
        Whether the item is [`FromRobTop`][gd.internals.robtop.protocols.FromRobTop].
    """
    return is_instance(item, FromRobTop)


@runtime_checkable
class ToRobTop(Protocol):
    """Represents types that can be converted to RobTop's format."""

    @required
    def to_robtop(self) -> str:
        ...


def is_to_robtop(item: Any) -> TypeGuard[ToRobTop]:
    """Checks if the given item is [`ToRobTop`][gd.internals.robtop.protocols.FromRobTop].

    Arguments:
        item: The item to check.

    Returns:
        Whether the item is [`ToRobTop`][gd.internals.robtop.protocols.FromRobTop].
    """
    return is_instance(item, ToRobTop)


@runtime_checkable
class RobTop(FromRobTop, ToRobTop, Protocol):
    """Represents types that implement both [`FromRobTop`][gd.internals.robtop.protocols.FromRobTop]
    and [`ToRobTop`][gd.internals.robtop.protocols.ToRobTop].
    """
