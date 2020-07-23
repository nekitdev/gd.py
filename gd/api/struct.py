from gd.utils.text_tools import make_repr
from gd.errors import EditorError

from gd.utils import search_utils as search

from gd.api.parser import (
    _dump,
    _convert,
    _collect,
    _process_level,
    _level_dump,
    _object_dump,
    _object_convert,
    _object_collect,
    _color_dump,
    _color_convert,
    _color_collect,
    _header_dump,
    _header_convert,
    _header_collect,
)

from gd.api.utils import _make_color, _get_dir, _define_color, get_id, get_default
from gd.api._property import (
    _object_code,
    _color_code,
    _header_code,
    _level_code,
)

from gd.typing import (
    Any,
    Color,
    ColorChannel,
    ColorCollection,
    Dict,
    Editor,
    Header,
    Iterable,
    LevelAPI,
    Object,
    Optional,
    Struct,
    Tuple,
    Union,
)

__all__ = ("Object", "ColorChannel", "Header", "LevelAPI", "ColorCollection", "DEFAULT_COLORS")

Number = Union[float, int]


class Struct:
    _dump = _dump
    _convert = _convert
    _convert = _collect
    _base_data = {}
    _container = {}

    def __init__(self, **properties) -> None:
        self.data = self._base_data.copy()

        for name, value in properties.items():
            setattr(self, name, value)

    def __repr__(self) -> str:
        info = {key: repr(value) for key, value in self.to_dict().items()}
        return make_repr(self, info)

    def __json__(self) -> Dict[str, Any]:
        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        final = {}
        for key, value in self.data.items():
            key = self._container.get(key)

            if key is not None:
                final[key] = value

        return final

    def dump(self) -> str:
        return self.__class__._collect(self.to_map())

    def to_map(self) -> Dict[str, Any]:
        return self.__class__._dump(self.data)

    def copy(self) -> Struct:
        self_copy = self.__class__()
        self_copy.data = self.data.copy()
        return self_copy

    def delete(self, *attrs) -> Struct:
        for attr in attrs:
            delattr(self, attr)
        return self

    def edit(self, **fields) -> Struct:
        for field, value in fields.items():
            setattr(self, field, value)
        return self

    @classmethod
    def from_mapping(cls, mapping: dict) -> Struct:
        self = cls()
        self.data = mapping
        return self

    @classmethod
    def from_string(cls, string: str) -> Struct:
        try:
            return cls.from_mapping(cls._convert(string))

        except Exception as exc:
            raise EditorError("Failed to process string.") from exc


class Object(Struct):
    _base_data = get_default("object")
    _dump = _object_dump
    _convert = _object_convert
    _collect = _object_collect

    def set_id(self, directive: str) -> Object:
        """Set ``id`` of ``self`` according to the directive, e.g. ``trigger:move``."""
        self.edit(id=get_id(directive))
        return self

    def set_z_layer(self, directive: str) -> Object:
        """Set ``z_layer`` of ``self`` according to the directive, e.g. ``layer:t1`` or ``b3``."""
        self.edit(z_layer=get_id(_get_dir(directive, "layer"), ret_enum=True))
        return self

    def set_easing(self, directive: str) -> Object:
        """Set ``easing`` of ``self`` according to the directive, e.g. ``sine_in_out``."""
        self.edit(easing=get_id(_get_dir(directive, "easing"), ret_enum=True))
        return self

    def set_color(self, color: Any) -> Object:
        """Set ``rgb`` of ``self`` to ``color``."""
        self.edit(**zip("rgb", _define_color(color).to_rgb()))
        return self

    def get_color(self) -> Color:
        """Attempt to get color of ``self``."""
        return _make_color(self)

    def add_groups(self, *groups: Iterable[int]) -> Object:
        """Add ``groups`` to ``self.groups``."""
        if self.groups is None:
            self.groups = set(groups)

        else:
            self.groups.update(groups)

        return self

    def get_pos(self) -> Tuple[Number, Number]:
        """Tuple[Union[:class:`float`, :class:`int`], Union[:class:`float`, :class:`int`]]:
        ``x`` and ``y`` coordinates of ``self``.
        """
        return (self.x, self.y)

    def set_pos(self, x: Number, y: Number) -> Object:
        """Set ``x`` and ``y`` position of ``self`` to given values."""
        self.x, self.y = x, y
        return self

    def move(self, x: Number = 0, y: Number = 0) -> Object:
        """Add ``x`` and ``y`` to coordinates of ``self``."""
        self.x += x
        self.y += y
        return self

    def rotate(self, deg: Number = 0) -> Object:
        """Add ``deg`` to ``rotation`` of ``self``."""
        if self.rotation is None:
            self.rotation = deg
        else:
            self.rotation += deg

        return self

    def is_checked(self):
        """:class:`bool`: indicates if ``self.portal_checked`` is true."""
        return bool(self.portal_checked)

    exec(_object_code)


class ColorChannel(Struct):
    _base_data = get_default("color_channel")
    _dump = _color_dump
    _convert = _color_convert
    _collect = _color_collect

    def __init__(self, special_directive: str = None, **properties) -> None:
        super().__init__(**properties)

        if special_directive is not None:
            self.set_id(special_directive)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Struct) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.data == other.data

    def set_id(self, directive: str) -> ColorChannel:
        """Set ColorID of ``self`` according to the directive, e.g. ``BG`` or ``color:bg``."""
        self.edit(id=get_id(_get_dir(directive, "color")))
        return self

    def set_color(self, color: Any) -> ColorChannel:
        """Set ``rgb`` of ``self`` to ``color``."""
        self.edit(**dict(zip("rgb", _define_color(color).to_rgb())))
        return self

    def get_color(self) -> Color:
        """Attempt to get color of ``self``."""
        return _make_color(self)

    exec(_color_code)


def _process_color(color: Union[str, Dict[str, Any], ColorChannel]):
    if isinstance(color, ColorChannel):
        return color
    elif isinstance(color, dict):
        return ColorChannel.from_mapping(color)
    elif isinstance(color, str):
        return ColorChannel.from_string(color)


class ColorCollection(set):
    @classmethod
    def create(cls, colors: Iterable[Any]) -> ColorCollection:
        if isinstance(colors, cls):
            return colors.copy()

        self = cls()
        self.update(colors)

        return self

    @classmethod
    def from_args(cls, *args) -> ColorCollection:
        return cls.create(args)

    def get(self, directive_or_id: Union[int, str]) -> Optional[ColorCollection]:
        final = directive_or_id
        if isinstance(final, str):
            final = get_id(_get_dir(final, "color"))
        return search.get(self, id=final)

    def copy(self) -> ColorCollection:
        return self.__class__(self)

    def update(self, colors: Iterable[ColorCollection]) -> None:
        super().update(color for color in map(_process_color, colors) if color is not None)

    def add(self, color: Any) -> None:
        color = _process_color(color)
        if color is not None:
            super().add(color)

    def __getitem__(self, color_id: int) -> Optional[ColorCollection]:
        return self.get(color_id)

    def dump(self) -> Iterable[Dict[str, Any]]:
        return [cc.data for cc in self]


DEFAULT_COLORS = [
    ColorChannel("BG").set_color(0x287DFF),
    ColorChannel("GRND").set_color(0x0066FF),
    ColorChannel("Line").set_color(0xFFFFFF),
    ColorChannel("P1").set_color(0x7DFF00),
    ColorChannel("P2").set_color(0x00FFFF),
    ColorChannel("GRND2").set_color(0x0066FF),
]


class Header(Struct):
    _base_data = get_default("header")
    _dump = _header_dump
    _convert = _header_convert
    _collect = _header_collect

    def __init__(self, **properties) -> None:
        super().__init__(**properties)
        self.colorhook()

    def copy(self) -> Header:
        copy = super().copy()

        if self.colors:
            copy.edit(colors=self.copy_colors())

        return copy

    def copy_colors(self) -> ColorCollection:
        if not self.colors:
            return ColorCollection()
        return ColorCollection(color.copy() for color in self.colors)

    def colorhook(self) -> None:
        if not self.colors:
            self.colors = ColorCollection.create(DEFAULT_COLORS)
        else:
            self.colors = ColorCollection.create(self.colors)

    @classmethod
    def from_mapping(cls, mapping) -> Header:
        self = super().from_mapping(mapping)
        self.colorhook()
        return self

    def dump(self) -> str:
        header = self.copy()

        if self.colors:
            header.edit(colors=self.colors.dump())

        return super(type(header), header).dump()

    exec(_header_code)


class LevelAPI(Struct):
    _convert = None
    _collect = None
    _dump = _level_dump
    _base_data = get_default("api")

    def __init__(self, **properties) -> None:
        super().__init__(**properties)

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "version": self.version,
            "name": self.name,
        }
        return make_repr(self, info)

    def dump(self) -> None:
        raise EditorError("Level API can not be dumped.")

    def open_editor(self) -> Editor:
        from gd.api.editor import Editor  # *circular imports*

        return Editor.launch(self, "level_string")

    def is_verified(self) -> bool:
        return bool(self.verified)

    def is_uploaded(self) -> bool:
        return bool(self.uploaded)

    def is_original(self) -> bool:
        return bool(self.original)

    def is_unlisted(self) -> bool:
        return bool(self.unlisted)

    @classmethod
    def from_mapping(cls, mapping) -> LevelAPI:
        self = cls()
        self.data = _process_level(mapping)
        return self

    @classmethod
    def from_string(cls, string: str) -> None:
        raise EditorError("Level API can not be created from string.")

    exec(_level_code)
