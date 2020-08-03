import functools

from attr import attrib, attrs, NOTHING

from gd.typing import Callable, Dict, Optional, Tuple, Type, TypeVar, Union

from gd.utils.enums import Enum
from gd.utils.text_tools import make_repr

ANNOTATIONS = "__annotations__"

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
        name: Optional[str] = None,
        type: Type[T] = object,
        default: Union[T, NULL] = null,
    ) -> None:
        self._index = str(index)
        self._converter = converter
        self._name = name
        self._type = type
        self._default = default

    def __repr__(self) -> str:
        info = {
            "index": self.index,
            "name": self.name,
            "type": self.type.__name__,
            "default": repr(self.default),
        }

        return make_repr(self, info)

    @property
    def index(self) -> str:
        return self._index

    @property
    def converter(self) -> Callable[[str], T]:
        return self._converter

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def type(self) -> Type[T]:
        return self._type

    @property
    def default(self) -> Optional[T]:
        return self._default

    def convert(self, value: U) -> T:
        return self.converter(value)


field = Field


class ModelStyle(Enum):
    NORMAL = 0
    MAP = 1
    ATTRS = 2
    DEFAULT = ATTRS

    def is_normal(self) -> bool:
        return self is self.NORMAL

    def is_map(self) -> bool:
        return self is self.MAP

    def is_attrs(self) -> bool:
        return self is self.ATTRS

    def is_default(self) -> bool:
        return self is self.DEFAULT


class ModelDict(dict):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._fields: Dict[str, Field] = {}

    def __setitem__(self, key: str, value: T) -> None:
        if isinstance(value, Field):
            self._fields[key] = value

        super().__setitem__(key, value)

    def copy(self) -> Dict[str, T]:
        return self.__class__(super().copy())

    @property
    def fields(self) -> Dict[str, Field]:
        return self._fields


class ModelMeta(type):
    @classmethod
    def __prepare__(meta_cls, cls_name: str, bases: Tuple[Type[T], ...], **kwargs) -> Dict[str, U]:
        style = ModelStyle.from_value(kwargs.get("style", "default"))

        if style.is_normal():
            return {}

        return ModelDict()

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[T], ...],
        cls_dict: Dict[str, U],
        style: Union[int, str, ModelStyle] = ModelStyle.DEFAULT,
    ) -> Type[Model_T]:
        style = ModelStyle.from_value(style)

        if style.is_normal():
            return super().__new__(meta_cls, cls_name, bases, cls_dict)

        annotations = cls_dict.get(ANNOTATIONS, {})
        fields = cls_dict.fields

        for name, field in fields.items():
            cls_dict.pop(name, None)

            field._name = name
            field._type = annotations.get(name, field._type)

        if style.is_attrs():
            cls = use_attrs_backend(meta_cls, bases, cls_dict, fields)

        elif style.is_map():
            ...

        else:
            raise ValueError(f"Do not know how to process style: {style!r}.")

        write_class_name(cls, cls_name)

        return cls


def write_class_name(cls: Type[T], name: str) -> None:
    cls.__qualname__ = cls.__name__ = name


def use_attrs_backend(
    meta_cls: Type[Type[Model_T]],
    bases: Tuple[Type[T], ...],
    cls_dict: Dict[str, U],
    field_map: Dict[str, Field],
) -> Type[Model_T]:
    @attrs
    class AttrsModel(*bases, metaclass=ModelMeta, style="normal"):
        nonlocal cls_dict, field_map

        FIELD_MAP = field_map
        FIELDS = list(FIELD_MAP.values())
        INDEX_TO_NAME = {field.index: field.name for field in FIELDS}

        namespace = vars()
        namespace.update(cls_dict)

        if FIELDS:
            for field in FIELDS:
                namespace[field.name] = attrib(
                    default=(
                        field.default if field.default is not null else NOTHING
                    ),
                    converter=field.converter,
                    type=field.type
                )

            del name, field

        del namespace

    return AttrsModel
