from abc import abstractmethod
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

R = TypeVar("R", covariant=True)


@runtime_checkable
class Read(Protocol[R]):
    @classmethod
    @abstractmethod
    def read_from(cls: Type[T], state: "BaseState", address: int) -> T:
        ...

    @classmethod
    @abstractmethod
    def read_value_from(cls, state: "BaseState", address: int) -> R:
        ...


W = TypeVar("W", contravariant=True)

@runtime_checkable
class Write(Protocol[W]):
    def write_to(self, state: "BaseState", address: int) -> None:
        ...

    @classmethod
    def write_value_to(cls, value: W, state: "BaseState", address: int) -> None:
        ...


class LayoutType(type(Protocol)):  # type: ignore
    @property
    @abstractmethod
    def size(cls) -> int:
        ...

    @property
    @abstractmethod
    def alignment(cls) -> int:
        ...


class Layout(metaclass=LayoutType):
    @class_property
    @abstractmethod
    def size(self) -> int:
        ...

    @class_property
    @abstractmethod
    def alignment(self) -> int:
        ...


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
