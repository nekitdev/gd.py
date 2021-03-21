# type: ignore  # static type checker will not understand this either

import re

from copy import deepcopy as recurse_copy
from functools import partial, wraps
from urllib.parse import quote, unquote

from gd.color import Color
from gd.crypto import (
    Key,
    decode_base64_str,
    decode_robtop_str,
    encode_base64_str,
    encode_robtop_str,
)
from gd.datetime import de_human_delta, ser_human_delta, datetime
from gd.enums import Enum
from gd.errors import DeError, SerError
from gd.index_parser import IndexParser, chain_from_iterable, group
from gd.map_property import map_property
from gd.text_utils import make_repr
from gd.typing import (
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

__all__ = (
    "BaseField",
    "Field",
    "Base64Field",
    "BoolField",
    "ColorField",
    "EnumField",
    "FloatField",
    "IntField",
    "IterableField",
    "MappingField",
    "ModelField",
    "ModelIterField",
    "RobTopStrField",
    "RobTopTimeField",
    "StrField",
    "URLField",
    "IndexParser",
    "Model",
    "attempt",
    "identity",
    "null",
    "partial",
    "recurse",
    "de_base64_str",
    "ser_base64_str",
    "de_bool_strict",
    "de_bool_soft",
    "de_bool",
    "ser_bool",
    "de_bytes",
    "ser_bytes",
    "de_color_rgb",
    "ser_color_rgb",
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
    "de_timestamp",
    "ser_timestamp",
)

# DO NOT CHANGE
DATA = "DATA"
EMPTY = ""

K = TypeVar("K")
V = TypeVar("V")
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

        return cls.instance


class NULL(Singleton):
    pass


null = NULL()


class RECURSE(Singleton):
    pass


recurse = RECURSE()


def try_several(*functions: Callable[..., T]) -> Callable[..., T]:
    def decorator(*args, **kwargs) -> T:
        for function in functions:
            try:
                return function(*args, **kwargs)

            except Exception:
                pass

        else:
            raise ValueError("All attempts have failed.")

    return decorator


def attempt(function: Callable[..., T], default: T) -> Callable[..., T]:
    @wraps(function)
    def wrapper(*args, **kwargs) -> T:
        try:
            return function(*args, **kwargs)

        except Exception:  # noqa
            return default

    return wrapper


def attempt_or(function: Callable[..., T], factory: Callable[[], T]) -> Callable[..., T]:
    @wraps(function)
    def wrapper(*args, **kwargs) -> T:
        try:
            return function(*args, **kwargs)

        except Exception:  # noqa
            return factory()

    return wrapper


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


def de_bool_soft(string_or_bool: Union[bool, str]) -> bool:
    if not string_or_bool:
        return False

    return string_or_bool != "0"


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


def de_iterable(
    string: str,
    delim: str,
    de: Callable[[str], T],
    transform: Callable[[Iterator[T]], Iterable[T]],
    skip_empty: bool = True,
) -> Iterable[T]:
    iterator = iter(string.split(delim))

    if skip_empty:
        iterator = filter(bool, iterator)

    iterator = map(de, iterator)

    return transform(iterator)


def ser_iterable(iterable: Iterable[T], delim: str, ser: Callable[[T], str]) -> str:
    return delim.join(map(ser, iterable))


def de_mapping(
    string: str,
    delim: str,
    de_key: Callable[[str], K],
    de_value: Callable[[str], V],
    transform: Callable[[Iterator[Tuple[K, V]]], Mapping[K, V]],
    skip_empty: bool = False,
) -> Mapping[K, V]:
    iterator = group(string.split(delim))

    if skip_empty:
        iterator = ((key, value) for key, value in iterator if key and value)

    return transform((de_key(key), de_value(value)) for key, value in iterator)


def ser_mapping(
    mapping: Mapping[K, V], delim: str, ser_key: Callable[[K], str], ser_value: Callable[[V], str]
) -> str:
    return delim.join(
        chain_from_iterable((ser_key(key), ser_value(value)) for key, value in mapping.items())
    )


def de_color_rgb(string: str, delim: str = ",") -> Color:
    return Color.from_rgb_string(string, delim)


def ser_color_rgb(color: Color, delim: str = ",") -> str:
    return delim.join(map(str, color.to_rgb()))


def de_enum(string: str, enum_type: Type[Enum], de_func: Callable[[str], T]) -> Enum:
    return enum_type(de_func(string))


def ser_enum(enum_member: Enum, ser_func: Callable[[T], str]) -> str:
    return ser_func(enum_member.value)


def de_model(string: str, model: Type["Model"], use_default: bool = False) -> "Model":
    return model.from_string(string, use_default=use_default)


def ser_model(model: "Model") -> str:
    return model.to_string()


de_base64_str = decode_base64_str
ser_base64_str = encode_base64_str


de_url = unquote
ser_url = partial(quote, safe=EMPTY)


common_pattern = re.compile(
    r"(?P<day>[0-9]+).(?P<month>[0-9]+).(?P<year>[0-9]+) "
    r"(?P<hour>[0-9]+).(?P<minute>[0-9]+)"
)


def de_common(string: str) -> datetime:
    match = common_pattern.match(string)

    if match is None:
        raise ValueError(f"{string!r} does not match the common pattern.")

    mapping = {name: int(value) for name, value in match.groupdict().items()}

    return datetime(**mapping)


def de_timestamp(string: str) -> datetime:
    return datetime.fromtimestamp(int(string))


def ser_timestamp(value: datetime) -> datetime:
    return value.timestamp()


def compose(function: Callable[[T], U], other: Callable[..., T]) -> Callable[..., U]:
    def composer(*args, **kwargs) -> U:
        return function(other(*args, **kwargs))

    return composer


class BaseField:
    def __init__(
        self,
        index: Union[int, str],
        de: Callable[[U], T],
        ser: Callable[[T], U],
        name: Optional[str] = None,
        type: Type[T] = object,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        self._index = str(index)

        if use_default_on_fail:
            if default is null:
                if factory is None:
                    raise ValueError(
                        "use_default_on_fail is specified, "
                        "while default and factory are not present."
                    )

                else:
                    de = attempt_or(de, factory)
                    ser = attempt_or(ser, compose(ser, factory))

            else:
                de = attempt(de, default)
                ser = attempt(ser, ser(default))

        self._de = de
        self._ser = ser
        self._name = name
        self._type = type
        self._default = default
        self._factory = factory
        self._doc = doc
        self._aliases = tuple(aliases)

    def __repr__(self) -> str:
        info = {
            "index": self.index,
            "name": self.name,
            "de": getattr(self.de, "__qualname__", self.de),
            "ser": getattr(self.ser, "__qualname__", self.ser),
            "type": getattr(self.type, "__name__", self.type),
            "default": repr(self.default),
            "aliases": self.aliases,
        }

        return make_repr(self, info)

    @property
    def index(self) -> str:
        return self._index

    @property
    def de(self) -> Callable[[U], T]:
        return self._de

    @property
    def ser(self) -> Callable[[T], U]:
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

    @property
    def factory(self) -> Optional[Callable[[], T]]:
        return self._factory

    @property
    def doc(self) -> Optional[str]:
        return self._doc

    @property
    def aliases(self) -> Tuple[str]:
        return self._aliases

    def deserialize(self, value: U) -> T:
        return self.de(value)

    def serialize(self, value: T) -> U:
        return self.ser(value)


class Field(BaseField):
    def __init__(
        self,
        index: Union[int, str],
        de: Callable[[str], T] = identity,
        ser: Callable[[T], str] = str,
        name: Optional[str] = None,
        type: Type[T] = object,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de,
            ser=ser,
            name=name,
            type=type,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class Base64Field(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        use_default_on_fail: bool = False,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_base64_str,
            ser=ser_base64_str,
            name=name,
            type=str,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class BoolField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        false: str = "0",
        true: str = "1",
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_bool,
            ser=partial(ser_bool, false=false, true=true),
            name=name,
            type=bool,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class ColorField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_color_rgb,
            ser=ser_color_rgb,
            name=name,
            type=Color,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class EnumField(Field):
    def __init__(
        self,
        index: Union[int, str],
        enum_type: Type[Enum],
        de: Callable[[str], T] = identity,
        ser: Callable[[T], str] = str,
        from_field: Optional[Type[Field]] = None,
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        if from_field is not None:
            field = from_field(index=index)
            de, ser = field.de, field.ser

        super().__init__(
            index=index,
            de=partial(de_enum, enum_type=enum_type, de_func=de),
            ser=partial(ser_enum, ser_func=ser),
            name=name,
            type=enum_type,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class IterableField(Field):
    def __init__(
        self,
        index: Union[int, str],
        delim: str,
        transform: Callable[[Iterator[T]], Iterable[T]],
        de: Callable[[str], T] = identity,
        ser: Callable[[T], str] = str,
        from_field: Optional[Type[Field]] = None,
        skip_empty: bool = True,
        name: Optional[str] = None,
        type: Type[U] = object,
        default: Union[U, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        if from_field is not None:
            field = from_field(index=index)
            de, ser = field.de, field.ser

        super().__init__(
            index=index,
            de=partial(
                de_iterable, delim=delim, de=de, transform=transform, skip_empty=skip_empty,
            ),
            ser=partial(ser_iterable, delim=delim, ser=ser),
            name=name,
            type=type,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class ModelIterField(IterableField):
    def __init__(
        self,
        index: Union[int, str],
        model: Type["Model"],
        delim: str,
        transform: Callable[[Iterator[T]], Iterable[T]],
        skip_empty: bool = True,
        use_default: bool = False,
        name: Optional[str] = None,
        type: Type[U] = object,
        default: Union[U, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            delim=delim,
            transform=transform,
            de=partial(de_model, model=model, use_default=use_default),
            ser=ser_model,
            skip_empty=skip_empty,
            name=name,
            type=type,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class MappingField(Field):
    def __init__(
        self,
        index: Union[int, str],
        delim: str,
        transform: Callable[[Iterator[Tuple[K, V]]], Mapping[K, V]],
        de_key: Callable[[str], K] = identity,
        de_value: Callable[[str], V] = identity,
        ser_key: Callable[[K], str] = str,
        ser_value: Callable[[V], str] = str,
        key_from_field: Optional[Type[Field]] = None,
        value_from_field: Optional[Type[Field]] = None,
        skip_empty: bool = False,
        name: Optional[str] = None,
        type: Type[U] = object,
        default: Union[U, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        if key_from_field is not None:
            field = key_from_field(index=index)
            de_key, ser_key = field.de, field.ser

        if value_from_field is not None:
            field = value_from_field(index=index)
            de_value, ser_value = field.de, field.ser

        super().__init__(
            index=index,
            de=partial(
                de_mapping,
                delim=delim,
                de_key=de_key,
                de_value=de_value,
                transform=transform,
                skip_empty=skip_empty,
            ),
            ser=partial(ser_mapping, delim=delim, ser_key=ser_key, ser_value=ser_value),
            name=name,
            type=type,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class FloatField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_float,
            ser=ser_float,
            name=name,
            type=float,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class IntField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_int,
            ser=ser_int,
            name=name,
            type=int,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class ModelField(Field):
    def __init__(
        self,
        index: Union[int, str],
        model: Type["Model"],
        use_default: bool = False,
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=partial(de_model, model=model, use_default=use_default),
            ser=ser_model,
            name=name,
            type=model,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class RobTopStrField(Field):
    def __init__(
        self,
        index: Union[int, str],
        key: Key,
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=partial(decode_robtop_str, key=key),
            ser=partial(encode_robtop_str, key=key),
            name=name,
            type=str,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class RobTopTimeField(Field):
    # TODO: update this to be able to read time from different timestamps

    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        # default: Union[T, NULL] = null,
        # use_default_on_fail: bool = False,
        # factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=try_several(de_human_delta, de_common, de_timestamp),
            ser=ser_human_delta,
            name=name,
            type=Optional[datetime],
            default=None,  # special
            use_default_on_fail=True,  # special
            # factory=factory,  # special
            doc=doc,
            aliases=aliases,
        )


class StrField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_str,
            ser=ser_str,
            name=name,
            type=str,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


class URLField(Field):
    def __init__(
        self,
        index: Union[int, str],
        name: Optional[str] = None,
        default: Union[T, NULL] = null,
        use_default_on_fail: bool = False,
        factory: Optional[Callable[[], T]] = None,
        doc: Optional[str] = None,
        aliases: Iterable[str] = (),
    ) -> None:
        super().__init__(
            index=index,
            de=de_url,
            ser=ser_url,
            name=name,
            type=str,
            default=default,
            use_default_on_fail=use_default_on_fail,
            factory=factory,
            doc=doc,
            aliases=aliases,
        )


def deserialize_parts(
    data: Dict[str, U], field_map: Dict[str, BaseField]
) -> Generator[Tuple[str, T], None, None]:
    try:
        for key, part in data.items():
            field = field_map.get(key)

            if field:
                yield key, field.de(part)

            else:
                yield key, part

    except Exception as origin:  # noqa
        raise DeError(data=part, index=key, field=field, origin=origin) from None


def deserialize_data(data: Dict[str, U], field_map: Dict[str, BaseField]) -> Dict[str, T]:
    return dict(deserialize_parts(data, field_map))


def serialize_parts(
    data: Dict[str, T], field_map: Dict[str, BaseField], enforce_str: bool = False
) -> Generator[Tuple[str, U], None, None]:
    try:
        for key, part in data.items():
            field = field_map.get(key)

            if field:
                yield key, field.ser(part)

            elif enforce_str:
                yield key, f"{part}"

            else:
                yield key, part

    except Exception as origin:  # noqa
        raise SerError(data=part, index=key, field=field, origin=origin) from None


def serialize_data(
    data: Dict[str, T], field_map: Dict[str, BaseField], enforce_str: bool = False
) -> Dict[str, U]:
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
        self._fields: Dict[str, BaseField] = {}

    def __setitem__(self, key: str, value: T) -> None:
        if isinstance(value, BaseField):
            self._fields[key] = value

        super().__setitem__(key, value)

    def copy(self) -> Dict[str, T]:
        return self.__class__(super().copy())

    @property
    def fields(self) -> Dict[str, BaseField]:
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
    ) -> Type["Model"]:
        if is_normal:
            return super().__new__(meta_cls, cls_name, bases, cls_dict)

        fields = cls_dict.fields

        for name, field in fields.items():  # process names
            cls_dict.pop(name, None)
            field._name = name

        cls = create_class_backend(meta_cls, bases, cls_dict, fields)

        write_class_name(cls, cls_name)

        annotations = get_type_hints(cls)

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
    meta_cls: Type[Type["Model"]],
    bases: Tuple[Type[T], ...],
    cls_dict: Dict[str, U],
    field_map: Dict[str, BaseField],
) -> Type["Model"]:
    class ModelBackend(*bases, metaclass=meta_cls, is_normal=True):
        nonlocal cls_dict, field_map

        NAME_MAP = field_map
        FIELDS = list(field_map.values())
        INDEX_MAP = {field.index: field for field in FIELDS}
        INDEX_TO_NAME = {field.index: field.name for field in FIELDS}

        DEFAULTS = {field.name: field.default for field in FIELDS if field.default is not null}
        FACTORIES = {field.name: field.factory for field in FIELDS if field.factory is not None}

        namespace = vars()
        namespace.update(cls_dict)

        if FIELDS:
            for field in FIELDS:
                for field_name in (field.name, *field.aliases):
                    namespace[field_name] = map_property(
                        name=field_name, attr=DATA, key=field.index, type=field.type, doc=field.doc
                    )

            del field_name
            del field

        del namespace

    return ModelBackend


class Model(metaclass=ModelMeta):
    PARSER: Optional[IndexParser] = None
    NAME_MAP: Dict[str, BaseField] = {}
    INDEX_MAP: Dict[str, BaseField] = {}
    FIELDS: List[Field] = []
    INDEX_TO_NAME: Dict[str, str] = {}
    DEFAULTS: Dict[str, T] = {}
    FACTORIES: Dict[str, Callable[[], T]] = {}
    ENFORCE_STR: bool = True
    REPR_IGNORE: Set[str] = set()

    def __init__(self, *, use_default: bool = True, **kwargs) -> None:
        self.DATA = {}

        if use_default:
            members = {name: factory() for name, factory in self.FACTORIES.items()}
            members.update(self.DEFAULTS)
            members.update(kwargs)
        else:
            members = kwargs

        for name, member in members.items():
            setattr(self, name, member)

    def __repr__(self) -> str:
        info = {
            name: repr(value)
            for name, value in self.to_dict().items()
            if name not in self.REPR_IGNORE
        }

        return make_repr(self, info)

    def __eq__(self, other: "Model") -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.DATA == other.DATA

    def __ne__(self, other: "Model") -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.DATA != other.DATA

    def __hash__(self) -> int:
        return hash(tuple(self.DATA.items()))

    def __json__(self) -> Dict[str, T]:
        return self.to_dict()

    def delete(self, *attrs) -> "Model":
        for attr in attrs:
            delattr(self, attr)
        return self

    def edit(self, **fields) -> "Model":
        for field, value in fields.items():
            setattr(self, field, value)
        return self

    @classmethod
    def with_data(cls, data: Dict[str, T], use_default: bool = False) -> "Model":
        self = cls(use_default=use_default)
        self.DATA.update(data)
        return self

    @classmethod
    def deserialize_data(cls, data: Dict[str, U]) -> Dict[str, T]:
        return deserialize_data(data, cls.INDEX_MAP)

    @classmethod
    def serialize_data(cls, data: Dict[str, T]) -> Dict[str, U]:
        return serialize_data(data, cls.INDEX_MAP, cls.ENFORCE_STR)

    @classmethod
    def from_data(cls, data: Dict[str, U], use_default: bool = False) -> "Model":
        self = cls(use_default=use_default)

        self.DATA.update(self.deserialize_data(data))

        return self

    def to_data(self) -> Dict[str, U]:
        return self.serialize_data(self.DATA)

    @classmethod
    def from_string(cls, string: str, use_default: bool = False) -> "Model":
        parser = cls.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use parsing when PARSER is undefined.")

        self = cls.from_data(parser.parse(string), use_default=use_default)

        return self

    def to_string(self) -> str:
        parser = self.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use unparsing when PARSER is undefined.")

        return parser.unparse(self.to_data())

    @classmethod
    def from_dict(cls, arg_dict: Dict[str, T], use_default: bool = True, **kwargs) -> "Model":
        self = cls(use_default=use_default, **kwargs)

        for name, arg in arg_dict.items():
            setattr(self, name, arg)

        return self

    @classmethod
    def maybe_in(cls, string: str) -> bool:
        parser = cls.PARSER

        if parser is None:
            raise RuntimeError("Attempt to use check when PARSER is undefined.")

        return parser.delim in string

    def to_dict(self, allow_missing: bool = False) -> Dict[str, T]:
        return map_index_to_name(self.DATA, self.INDEX_TO_NAME, allow_missing)

    def __copy__(self) -> "Model":
        return self.with_data(self.DATA)
        return self.__class__.with_data(self.DATA)

    def __deepcopy__(self, memo: Optional[Dict[str, U]] = None) -> "Model":
        return self.with_data(recurse_copy(self.DATA, memo))

    copy = __copy__
    clone = __deepcopy__
