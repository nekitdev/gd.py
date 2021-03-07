from gd.memory.traits import Layout, ReadLayout, ReadWriteLayout
from gd.text_utils import make_repr
from gd.typing import Any, Generic, Literal, Optional, Type, TypeVar, Union, overload

__all__ = ("Field", "MutField")

UNSIZED = "unsized"
L = TypeVar("L", bound=Layout)
T = TypeVar("T")


class BaseField(Generic[L]):
    def __init__(self, type: Type[L], offset: int, frozen: bool = False) -> None:
        self._type = type
        self._offset = offset
        self._frozen = frozen

    def __repr__(self) -> str:
        try:
            size = self.size

        except TypeError:
            size = UNSIZED

        info = {"offset": self.offset, "size": size, "type": self.type.__name__}

        return make_repr(self, info)

    def get_offset(self) -> int:
        return self._offset

    def set_offset(self, offset: int) -> None:
        if self._frozen:
            raise TypeError("Can not update this field.")

        self._offset = offset

    offset = property(get_offset, set_offset)

    def get_type(self) -> Type[L]:
        return self._type

    def set_type(self, type: Type[L]) -> None:
        if self._frozen:
            raise TypeError("Can not update this field.")

        self._type = type

    type = property(get_type, set_type)

    def get_size(self) -> int:
        return self.type.size

    size = property(get_size)

    def get_alignment(self) -> int:
        return self.type.alignment

    alignment = property(get_alignment)

    def freeze(self) -> None:
        self._frozen = True

    def unfreeze(self) -> None:
        self._frozen = False


class Field(BaseField[ReadLayout[T]]):
    def __init__(self, type: Type[ReadLayout[T]], offset: int) -> None:
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


class MutField(Field[T], BaseField[ReadWriteLayout[T]]):
    def __init__(self, type: Type[ReadWriteLayout[T]], offset: int) -> None:
        super().__init__(type, offset)  # type: ignore

    def __set__(self, instance: Any, value: T) -> None:
        self.type.write_value_to(value, instance.state, instance.address + self.offset)

    def __delete__(self, instance: Any) -> None:
        raise AttributeError("Can not delete field.")
