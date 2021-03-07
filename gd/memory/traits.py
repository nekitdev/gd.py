from inspect import isclass as is_class

from gd.memory.utils import class_property
from gd.typing import TYPE_CHECKING, Any, Protocol, Type, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from gd.memory.state import BaseState  # noqa

__all__ = (
    "Layout",
    "Read",
    "Write",
    # common traits
    "Layout",
    "ReadLayout",
    "ReadWriteLayout",
    "WriteLayout",
    # useful functions
    "is_class",
    "is_layout",
)

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


class LayoutType(type(Protocol)):  # type: ignore
    @property
    def size(cls) -> int:
        raise NotImplementedError(
            "Classes derived from Layout must implement size property in class."
        )

    @property
    def alignment(cls) -> int:
        raise NotImplementedError(
            "Classes derived from Layout must implement alignment property in class."
        )


class Layout(Protocol[T_co], metaclass=LayoutType):
    @class_property
    def size(self: T_co) -> int:
        raise NotImplementedError("Classes derived from Layout must implement size property.")

    @class_property
    def alignment(self: T_co) -> int:
        raise NotImplementedError(
            "Classes derived from Layout must implement alignment property."
        )


class ReadLayout(Read[T], Layout[T]):
    pass


class ReadWriteLayout(Read[T], Write[T], Layout[T]):
    pass


class WriteLayout(Write[T], Layout[T]):
    pass


def is_sized(some: Any) -> bool:
    try:
        if is_class(some):
            return isinstance(some.size, int)

        else:
            return isinstance(some.size, int) and is_sized(some.__class__)

    except (AttributeError, NotImplementedError):
        return False

    except Exception:
        return True


def is_aligned(some: Any) -> bool:
    try:
        if is_class(some):
            return isinstance(some.alignment, int)

        else:
            return isinstance(some.alignment, int) and is_aligned(some.__class__)

    except (AttributeError, NotImplementedError):
        return False

    except Exception:
        return True


def is_layout(some: Any) -> bool:
    return is_sized(some) and is_aligned(some)
