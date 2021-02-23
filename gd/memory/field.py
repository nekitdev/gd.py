from gd.memory.common_traits import ReadSized, ReadWriteSized
from gd.memory.traits import Sized
from gd.text_utils import make_repr
from gd.typing import Any, Generic, Literal, Optional, Type, TypeVar, Union, overload

__all__ = ("Field", "MutField")

S = TypeVar("S", bound=Sized)
T = TypeVar("T")


class BaseField(Generic[S]):
    def __init__(self, type: Type[S], offset: int) -> None:
        self._type = type
        self._offset = offset

    def __repr__(self) -> str:
        info = {"offset": self.offset, "size": self.size, "type": self.type.__name__}

        return make_repr(self, info)

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def type(self) -> Type[S]:
        return self._type

    @property
    def size(self) -> int:
        return self.type.size


class Field(BaseField[ReadSized[T]]):
    def __init__(self, type: Type[ReadSized[T]], offset: int) -> None:
        super().__init__(type, offset)

    @overload  # noqa
    def __get__(  # noqa
        self, instance: Literal[None], owner: Optional[Type[Any]] = None
    ) -> "Field[T]":
        ...

    @overload  # noqa
    def __get__(self, instance: Any, owner: Optional[Type[Any]] = None) -> T:  # noqa
        ...

    def __get__(  # noqa
        self, instance: Optional[Any], owner: Optional[Type[Any]] = None
    ) -> Union[T, "Field[T]"]:
        if instance is None:
            return self

        return self.type.read_value_from(instance.state, instance.address + self.offset)

    def __set__(self, instance: Any, value: T) -> None:
        raise AttributeError("Can not set field, as it is immutable.")

    def __delete__(self, instance: Any) -> None:
        raise AttributeError("Can not delete field.")


class MutField(Field[T], BaseField[ReadWriteSized[T]]):
    def __init__(self, type: Type[ReadWriteSized[T]], offset: int) -> None:
        super().__init__(type, offset)  # type: ignore

    def __set__(self, instance: Any, value: T) -> None:
        self.type.write_value_to(value, instance.state, instance.address + self.offset)

    def __delete__(self, instance: Any) -> None:
        raise AttributeError("Can not delete field.")
