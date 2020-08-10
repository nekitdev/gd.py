from base64 import urlsafe_b64decode, urlsafe_b64encode
from functools import partial, wraps
from urllib.parse import quote, unquote

from gd.map_property import map_property

from gd.typing import Callable, Dict, Generator, List, Optional, Tuple, Type, TypeVar, Union

from gd.utils.enums import Enum
from gd.utils.index_parser import IndexParser
from gd.utils.text_tools import make_repr

__all__ = (
    "Field",
    "Base64Field",
    "BoolField",
    "FloatField",
    "IntField",
    "StrField",
    "URLField",
    "IndexParser",
    "Model",
    "attempt",
    "identity",
    "null",
    "partial",
    "recurse",
    "de_base64_bytes",
    "ser_base64_bytes",
    "de_base64_str",
    "ser_base64_str",
    "de_bool_strict",
    "de_bool_soft",
    "de_bool",
    "ser_bool",
    "de_bytes",
    "ser_bytes",
    "de_enum",
    "ser_enum",
    "de_float",
    "ser_float",
    "de_int",
    "ser_int",
    "de_str",
    "ser_str",
    "de_url",
    "ser_url",
)

# DO NOT CHANGE
ANNOTATIONS = "__annotations__"
DATA = "DATA"

Model_T = TypeVar("Model")
ModelList_T = TypeVar("ModelList")

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

    @wraps(func)
    def inner(*args, **kwargs) -> Optional[T]:
        try:
            return func(*args, **kwargs)

        except Exception:  # noqa
            return default

    return inner


def identity(some: T) -> T:
    return some


def de_bool_strict(string: str) -> bool:
    if not string:
        return False

    if string == "0":
        return False

    if string == "1":
        return True

    raise ValueError(f"String bool deserializing expected empty string, 0 or 1, got {string!r}.")


def de_bool_soft(string: str) -> bool:
    if not string:
        return False

    return string != "0"


de_bool = de_bool_soft


def ser_bool(value: bool, false: str = "0", true: str = "1") -> str:
    return true if value else false


de_float = float


def ser_float(value: float) -> str:
    truncated = int(value)

    return str(value if value != truncated else truncated)


de_int = int
ser_int = str

de_str = str
ser_str = str

de_bytes = str.encode
ser_bytes = bytes.decode


def de_enum(string: str, enum: Type[Enum], de_func: Callable[[str], T]) -> Enum:
    return enum(de_func(string))


def ser_enum(enum_member: Enum, ser_func: Callable[[T], str]) -> str:
    return ser_func(enum_member.value)


def de_model(string: str, model: Type[Model_T]) -> Model_T:
    return model.from_string(string)


def ser_model(model: Model_T) -> str:
    return model.to_string()


def de_base64_str(string: str) -> str:
    return de_base64_bytes(string).decode()


def de_base64_bytes(string: str) -> bytes:
    remain = len(string) % 4

    if remain:
        string += "=" * (4 - remain)

    return urlsafe_b64decode(string)


def ser_base64_str(string: str) -> str:
    return ser_base64_bytes(string.encode())


def ser_base64_bytes(string: bytes) -> str:
    return urlsafe_b64encode(string).decode()


de_url = unquote
ser_url = partial(quote, safe="")


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
            "ser": self.ser,
            "de": self.de,
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


class Base64Field(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index, de=de_base64_str, ser=ser_base64_str, name=name, type=str, default=default
        )


class BoolField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index, de=de_bool, ser=ser_bool, name=name, type=bool, default=default
        )


class FloatField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index, de=de_float, ser=ser_float, name=name, type=float, default=default
        )


class IntField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index, de=de_int, ser=ser_int, name=name, type=int, default=default
        )


class ModelField(Field):
    def __init__(
        self,
        index: Union[int, str],
        model: Type[Model_T],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index,
            de=partial(de_model, model=model),
            ser=ser_model,
            name=name,
            type=model,
            default=default,
        )


class StrField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index, de=de_str, ser=ser_str, name=name, type=str, default=default
        )


class URLField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
    ) -> None:
        super().__init__(
            index=index, de=de_url, ser=ser_url, name=name, type=str, default=default
        )


def deserialize_parts(data: Dict[str, str], field_map: Dict[str, Field]) -> Generator[Tuple[str, T], None, None]:
    for key, part in data.items():
        field = field_map.get(key)

        if field:
            yield key, field.deserialize(part)

        else:
            yield key, part


def deserialize_data(data: Dict[str, str], field_map: Dict[str, Field]) -> Dict[str, T]:
    return dict(deserialize_parts(data, field_map))


def serialize_parts(data: Dict[str, T], field_map: Dict[str, Field]) -> Generator[Tuple[str, str], None, None]:
    for key, part in data.items():
        field = field_map.get(key)

        if field:
            yield key, field.serialize(part)

        else:
            yield key, str(part)


def serialize_data(data: Dict[str, T], field_map: Dict[str, Field]) -> Dict[str, str]:
    return dict(serialize_parts(data, field_map))


def map_index_to_name_gen(
    data: Dict[str, T], index_to_name: Dict[str, str], allow_missing: bool = False
) -> Generator[Tuple[str, T], None, None]:
    for index, part in data.items():
        name = index_to_name.get(index)

        if name:
            yield name, part

        elif allow_missing:
            yield f"index_{index}", part

        # ... no need to use else


def map_index_to_name(
    data: Dict[str, T], index_to_name: Dict[str, str], allow_missing: bool = False
) -> Dict[str, T]:
    return dict(map_index_to_name_gen(data, index_to_name, allow_missing))


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

        for name, field in fields.items():  # process names
            cls_dict.pop(name, None)

            field._name = name

        cls = create_class_backend(meta_cls, bases, cls_dict, fields)

        write_class_name(cls, cls_name)

        for name, field in fields.items():  # process types
            field_type = annotations.get(name, field._type)

            if field_type is recurse:
                field_type = cls

            annotations[name] = field_type
            field._type = field_type

        return cls


def write_class_name(cls: Type[T], name: str) -> None:
    cls.__qualname__ = cls.__name__ = name


def create_class_backend(
    meta_cls: Type[Type[Model_T]],
    bases: Tuple[Type[T], ...],
    cls_dict: Dict[str, U],
    field_map: Dict[str, Field],
) -> Type[Model_T]:
    class ModelBackend(*bases, metaclass=meta_cls, is_normal=True):
        nonlocal cls_dict, field_map

        NAME_MAP = field_map
        FIELDS = list(field_map.values())
        INDEX_MAP = {field.index: field for field in FIELDS}
        INDEX_TO_NAME = {field.index: field.name for field in FIELDS}

        DEFAULTS = {field.name: field.default for field in FIELDS if field.default is not null}

        namespace = vars()
        namespace.update(cls_dict)

        if FIELDS:
            for field in FIELDS:
                namespace[field.name] = map_property(
                    name=field.name,
                    attr=DATA,
                    key=field.index,
                    type=field.type,
                    doc=f"Data field: {field.name}.",
                )
            del field

        del namespace

    return ModelBackend


class Model(metaclass=ModelMeta):
    PARSER: Optional[IndexParser] = None
    NAME_MAP: Dict[str, Field] = {}
    INDEX_MAP: Dict[str, Field] = {}
    FIELDS: List[Field] = []
    INDEX_TO_NAME: Dict[str, str] = {}

    def __init__(self, *, use_default: bool = True, **kwargs) -> None:
        self.DATA = {}

        if use_default:
            members = self.DEFAULTS.copy()
            members.update(kwargs)
        else:
            members = kwargs

        for name, member in members.items():
            setattr(self, name, member)

    def __repr__(self) -> str:
        info = {name: repr(value) for name, value in self.to_dict().items()}

        return make_repr(self, info)

    @classmethod
    def deserialize_data(cls, data: Dict[str, str]) -> Dict[str, T]:
        return deserialize_data(data, cls.INDEX_MAP)

    @classmethod
    def serialize_data(cls, data: Dict[str, T]) -> Dict[str, str]:
        return serialize_data(data, cls.INDEX_MAP)

    @classmethod
    def from_data(cls, data: Dict[str, str], use_default: bool = False) -> Model_T:
        self = cls(use_default=use_default)

        self.DATA.update(self.deserialize_data(data))

        return self

    def to_data(self) -> Dict[str, str]:
        return self.serialize_data(self.DATA)

    @classmethod
    def from_string(cls, string: str, use_default: bool = False) -> Model_T:
        parser = cls.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use parsing when PARSER is undefined.")

        return cls.from_data(parser.parse(string), use_default=use_default)

    def to_string(self) -> str:
        parser = self.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use unparsing when PARSER is undefined.")

        return parser.unparse(self.to_data())

    @classmethod
    def from_dict(cls, arg_dict: Dict[str, T], use_default: bool = True) -> Model_T:
        return cls(use_default=use_default, **arg_dict)

    def to_dict(self, allow_missing: bool = False) -> Dict[str, T]:
        return map_index_to_name(self.DATA, self.INDEX_TO_NAME, allow_missing)


class ModelListMeta(type):
    def __getitem__(cls, model_type: Type[Model]) -> Callable[..., ModelList_T]:
        return partial(cls, model_type=model_type)


class ModelList(metaclass=ModelListMeta):
    def __init__(self, delim: str, model_type: Type[Model]) -> None:
        self._model_type = model_type
        self._delim = delim

    def __repr__(self) -> str:
        info = {
            "model_type": self._model_type.__name__,
            "delim": repr(self._delim),
        }
        return make_repr(self, info)

    def from_string(self, string: str) -> List[Model]:
        return list(map(
            self._model_type.from_string,
            filter(bool, string.split(self._delim)),
        ))

    def to_string(self, models: List[Model]) -> str:
        return self._delim.join(map(
            self._model_type.to_string, models
        ))
