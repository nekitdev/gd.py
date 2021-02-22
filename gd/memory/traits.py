from inspect import isclass as is_class

from gd.memory.utils import class_property
from gd.typing import TYPE_CHECKING, Any, Protocol, Type, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = ("Sized", "Read", "Write", "is_class", "is_sized")

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


@runtime_checkable
class Read(Protocol[T_co]):
    @classmethod
    def read_from(cls: Type[T], state: "BaseState", address: int) -> T:
        raise NotImplementedError(
            "Classes derived from Read must implement read_from(state, address) class method."
        )

    @classmethod
    def read_value_from(cls, state: "BaseState", address: int) -> T_co:
        raise NotImplementedError(
            "Classes derived from Read must implement "
            "read_value_from(state, address) class method."
        )


@runtime_checkable
class Write(Protocol[T_contra]):
    def write_to(self: T, state: "BaseState", address: int) -> None:
        raise NotImplementedError(
            "Classes derived from Write must implement write_to(state, address) method."
        )

    @classmethod
    def write_value_to(cls, value: T_contra, state: "BaseState", address: int) -> None:
        raise NotImplementedError(
            "Classes derived from Write must implement "
            "write_value_to(value, state, address) class method."
        )


class SizedType(type(Protocol)):  # type: ignore
    @property
    def size(cls) -> int:
        raise NotImplementedError(
            "Classes derived from Sized must implement size property in class."
        )


class Sized(Protocol[T_co], metaclass=SizedType):
    @class_property
    def size(self: T_co) -> int:
        raise NotImplementedError("Classes derived from Sized must implement size property.")


def is_sized(some: Any) -> bool:
    try:
        if is_class(some):
            return isinstance(some.size, int)

        else:
            return isinstance(some.size, int) and is_sized(some.__class__)

    except (AttributeError, NotImplementedError):
        return False
