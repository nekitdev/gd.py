from gd.typing import Any, Callable, Generic, Iterator, Optional, TypeVar

__all__ = ("Option", "Some", "Null")

K = TypeVar("K")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class NullValueError(ValueError):
    pass


class Option(Generic[T]):
    def __init__(self, value: Optional[T]) -> None:
        self._value = value

    def __repr__(self) -> str:
        if self._value is None:
            return "Null"

        return f"{self.__class__.__name__}({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._value == other._value

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._value == other._value

    def __bool__(self) -> bool:
        return bool(self._value)

    def __hash__(self) -> int:
        return hash(self._value)

    def __call__(self, *args, **kwargs) -> "Option[U]":
        if callable(self._value):
            return self.__class__(self._value(*args, **kwargs))

        return self.__class__(None)  # type: ignore

    def __setattr__(self, name: str, value: V) -> None:
        if name == "_value":
            try:
                self.__getattribute__(name)  # if we reach code below, value exists already
                raise TypeError(f"Value of {self.__class__.__name__!r} is immutable.")

            except AttributeError:  # not set yet, allow setting
                pass

        super().__setattr__(name, value)

    def __getattr__(self, name: str) -> "Option[U]":
        return self.__class__(getattr(self._value, name, None))  # type: ignore

    def __getitem__(self, item: K) -> "Option[U]":
        try:
            return self.__class__(self._value[item])  # type: ignore

        except Exception:  # noqa
            return self.__class__(None)  # type: ignore

    def __setitem__(self, item: K, value: V) -> None:
        try:
            self._value[item] = value  # type: ignore

        except Exception:  # noqa
            pass

    def __delitem__(self, item: K) -> None:
        try:
            del self._value[item]  # type: ignore

        except Exception:  # noqa
            pass

    def __iter__(self) -> Iterator[T]:
        try:
            return iter(self._value)  # type: ignore

        except TypeError:
            return iter((self._value,))  # type: ignore

    def is_null(self) -> bool:
        return self._value is None

    def is_some(self) -> bool:
        return self._value is not None

    def get(self) -> Optional[T]:
        return self._value

    def unwrap(self) -> T:
        if self._value is None:
            raise NullValueError

        return self._value

    def unwrap_or(self, default: T) -> T:
        if self._value is None:
            return default

        return self._value

    def unwrap_or_else(self, default_function: Callable[[], T]) -> T:
        if self._value is None:
            return default_function()

        return self._value

    def contains(self, value: T) -> bool:
        return self._value == value

    def map(self, function: Callable[[T], U]) -> "Option[U]":
        if self._value is None:
            return self.__class__(None)  # type: ignore

        return self.__class__(function(self._value))  # type: ignore

    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        if self._value is None or not predicate(self._value):
            return self.__class__(None)  # type: ignore

        return self.__class__(self._value)  # type: ignore

    def then(self, function: Callable[[T], "Option[U]"]) -> "Option[U]":
        if self._value is None:
            return self.__class__(None)  # type: ignore

        return function(self._value)


class Some(Option):
    pass


Null = Some(None)
