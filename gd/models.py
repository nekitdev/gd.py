import functools

from gd.typing import Callable, Optional, Type, TypeVar, Union

from gd.utils.enums import Enum
from gd.utils.text_tools import make_repr

Model_T = TypeVar("Model")

T = TypeVar("T")
U = TypeVar("U")


class Singleton:
    instance = None

    def __repr__(self) -> str:  # pragma: no cover
        return make_repr(self)

    @classmethod
    def __new__(cls, *args, **kwargs) -> T:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init__(*args, **kwargs)
        return cls.instance


class NULL(Singleton):
    pass


null = NULL()


class RECURSE(Singleton):
    pass


recurse = RECURSE()


def attempt(func: Callable[..., T], default: Optional[T] = None) -> Callable[..., T]:

    @functools.wraps(func)
    def inner(*args, **kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)

        except Exception:  # noqa
            return default

    return inner


def identity(some: T) -> T:
    return some


def into_enum(enum: Enum, type: Optional[Type[T]]) -> Callable[[U], Enum]:
    def convert_to_enum(value: U) -> Enum:
        return enum(type(value))

    return convert_to_enum


class Field:
    def __init__(
        self,
        index: Union[int, str],
        converter: Callable[[str], T] = identity,
        type: Type[T] = object,
        default: Union[T, NULL] = null,
    ) -> None:
        self._index = str(index)
        self._converter = converter
        self._type = type
        self._default = default

        self._value = self._index

    @property
    def index(self) -> str:
        return self._index

    @property
    def converter(self) -> Callable[[str], T]:
        return self._converter

    @property
    def type(self) -> Type[T]:
        return self._type

    @property
    def default(self) -> Optional[T]:
        return self._default

    def __repr__(self) -> str:
        info = {
            "index": self.index,
            "type": self.type.__name__,
            "default": repr(self.default),
        }

        return make_repr(self, info)

    def convert(self, value: U) -> T:
        return self.converter(value)


field = Field
