import functools

from gd.map_property import map_property

from gd.typing import Callable, Dict, Generator, List, Optional, Tuple, Type, TypeVar, Union

from gd.utils.enums import Enum
from gd.utils.index_parser import IndexParser
from gd.utils.text_tools import make_repr

__all__ = ("Field", "IndexParser", "Model", "attempt", "identity", "into_enum", "null", "recurse")

# DO NOT CHANGE
ANNOTATIONS = "__annotations__"
DATA = "DATA"

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
        de: Callable[[str], T] = identity,
        ser: Callable[[T], str] = str,
        name: Optional[str] = None,
        type: Type[T] = object,
        default: Union[T, NULL] = null,
    ) -> None:
        self._index = str(index)
        self._de = de
        self._ser = ser
        self._name = name
        self._type = type
        self._default = default

    def __repr__(self) -> str:
        info = {
            "index": self.index,
            "name": self.name,
            "ser": self.ser.__name__,
            "de": self.de.__name__,
            "type": self.type.__name__,
            "default": repr(self.default),
        }

        return make_repr(self, info)

    @property
    def index(self) -> str:
        return self._index

    @property
    def de(self) -> Callable[[str], T]:
        return self._de

    @property
    def ser(self) -> Callable[[T], str]:
        return self._ser

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def type(self) -> Type[T]:
        return self._type

    @property
    def default(self) -> Optional[T]:
        return self._default

    def deserialize(self, string: str) -> T:
        return self.de(string)

    def serialize(self, value: T) -> str:
        return self.ser(value)


field = Field


def data_index_to_name(data: Dict[str, str], index_to_name: Dict[str, str], kwargs: Dict[str, T]) -> Dict[str, U]:
    data_kwargs = {
        index_to_name.get(index, index): part for index, part in data.items()
    }

    data_kwargs.update(kwargs)

    return data_kwargs


def data_name_to_index(data: Dict[str, str], name_to_index: Dict[str, str], kwargs: Dict[str, str]) -> Dict[str, str]:
    converted = {
        name_to_index.get(name, name): part for name, part in data.items()
    }

    converted.update({
        name_to_index.get(name, name) for name, part in kwargs.items()
    })

    return converted


def deserialize_parts(data: Dict[str, str], field_map: Dict[str, Field]) -> Generator[Tuple[str, T], None, None]:
    for name, part in data.items():
        field = field_map.get(name)

        if field:
            yield name, field.deserialize(part)

        else:
            yield name, part


def deserialize_data(data: Dict[str, str], field_map: Dict[str, Field]) -> Dict[str, T]:
    return dict(deserialize_parts(data, field_map))


def serialize_parts(data: Dict[str, T], field_map: Dict[str, Field]) -> Generator[Tuple[str, str], None, None]:
    for name, part in data.items():
        field = field_map.get(name)

        if field:
            yield name, field.serialize(part)

        else:
            yield name, str(part)


def serialize_data(data: Dict[str, T], field_map: Dict[str, Field]) -> Dict[str, str]:
    return dict(serialize_parts(data, field_map))


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
        is_normal = kwargs.get("is_normal")

        if is_normal:
            return {}

        return ModelDict()

    def __new__(
        meta_cls,
        cls_name: str,
        bases: Tuple[Type[T], ...],
        cls_dict: Dict[str, U],
        is_normal: bool = False,
    ) -> Type[Model_T]:
        if is_normal:
            return super().__new__(meta_cls, cls_name, bases, cls_dict)

        annotations = cls_dict.get(ANNOTATIONS, {})
        fields = cls_dict.fields

        for name, field in fields.items():
            cls_dict.pop(name, None)

            field._name = name
            field._type = annotations.get(name, field._type)

        cls = create_map_backend(meta_cls, bases, cls_dict, fields)

        write_class_name(cls, cls_name)

        return cls


def write_class_name(cls: Type[T], name: str) -> None:
    cls.__qualname__ = cls.__name__ = name


def create_map_backend(
    meta_cls: Type[Type[Model_T]],
    bases: Tuple[Type[T], ...],
    cls_dict: Dict[str, U],
    field_map: Dict[str, Field],
) -> Type[Model_T]:
    class MapModel(*bases, metaclass=meta_cls, is_normal=True):
        nonlocal cls_dict, field_map

        FIELD_MAP = field_map
        FIELDS = list(FIELD_MAP.values())
        INDEX_TO_NAME = {field.index: field.name for field in FIELDS}
        NAME_TO_INDEX = {name: index for index, name in INDEX_TO_NAME.items()}

        DEFAULTS = {field.name: field.default for field in FIELDS if field.default is not null}

        namespace = vars()
        namespace.update(cls_dict)

        if FIELDS:
            for field in FIELDS:
                namespace[field.name] = map_property(
                    name=field.name,
                    attr=DATA,
                    key=field.name,
                    type=field.type,
                    doc=f"Data field: {field.name}.",
                )
            del field

        del namespace

    return MapModel


class Model(metaclass=ModelMeta):
    PARSER: Optional[IndexParser] = None
    FIELD_MAP: Dict[str, Field] = {}
    FIELDS: List[Field] = []
    INDEX_TO_NAME: Dict[str, str] = {}
    NAME_TO_INDEX: Dict[str, str] = {}

    def __init__(self, **members) -> None:
        data = self.DEFAULTS.copy()
        data.update(members)

        self.DATA = deserialize_data(data, self.FIELD_MAP)

    def __repr__(self) -> str:
        return make_repr(self, self.to_dict())

    @classmethod
    def from_data(cls, data: Dict[str, str], **kwargs) -> Model_T:
        return cls(**data_index_to_name(data, cls.INDEX_TO_NAME, kwargs))

    def to_data(self, **kwargs) -> Dict[str, str]:
        data = serialize_data(self.DATA, self.FIELD_MAP)
        return data_name_to_index(data, self.NAME_TO_INDEX, kwargs)

    @classmethod
    def from_string(cls, string: str, **kwargs) -> Model_T:
        parser = cls.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use parsing when PARSER is undefined.")

        return cls.from_data(parser.parse(string), **kwargs)

    def to_string(self, **kwargs) -> str:
        parser = self.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use unparsing when PARSER is undefined.")

        return parser.unparse(self.to_data(**kwargs))

    def to_dict(self) -> Dict[str, T]:
        field_map = self.FIELD_MAP

        return {name: part for name, part in self.DATA.items() if name in field_map}
