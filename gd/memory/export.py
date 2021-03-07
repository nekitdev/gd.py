from gd.typing import Any, Generic, Optional, Type, TypeVar, Union

__all__ = ("Export", "export", "is_export")

T = TypeVar("T")


class Export(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"

    @property
    def value(self) -> T:
        return self._value

    def __get__(self, instance: Optional[Any], owner: Optional[Type[Any]] = None) -> Any:
        try:
            return self.value.__get__(instance, owner)  # type: ignore

        except AttributeError:
            return self.value

    def __set__(self, instance: Any, value: Any) -> None:
        try:
            return self.value.__set__(instance, value)  # type: ignore

        except AttributeError:
            pass

        raise AttributeError("Attribute is read-only.")

    def __delete__(self, instance: Any) -> None:
        try:
            return self.value.__delete__(instance)  # type: ignore

        except AttributeError:
            pass

        raise AttributeError("Attribute is read-only.")


def export(some: T) -> Export[T]:
    return Export(some)


def is_export(some: Union[T, Export[T]]) -> bool:  # noqa
    return isinstance(some, Export)
