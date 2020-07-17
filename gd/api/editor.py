from gd.typing import (
    Any,
    Callable,
    Dict,
    Editor,
    Iterable,
    Iterator,
    Level,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from gd.api.enums import (
    SpeedMagic,
    Speed,
    PortalType,
)
from gd.api.struct import Object, ColorChannel, Header, ColorCollection, LevelAPI

from gd.errors import EditorError
from gd.utils.text_tools import make_repr

__all__ = ("Editor", "get_length_from_x")

speed_map = {}

for string in ("slow", "normal", "fast", "faster", "fastest"):
    magic, speed, portal = (
        SpeedMagic.from_name(string),
        Speed.from_name(string),
        PortalType.from_name(string + "speed"),
    )
    speed_map.update({speed.value: magic.value, portal.value: magic.value})

del string, magic, speed, portal

_portals = {enum.value for enum in PortalType}
_speed_protals = {enum.value for enum in PortalType if ("speed" in enum.name.lower())}


def get_length_from_x(dx: float, start_speed: Speed, portals: Sequence[Object]) -> float:
    """Calculate amount of time (length).

    Computes the time (in seconds) to travel from ``0`` to ``dx`` on x axis,
    respecting speed portals.

    Parameters
    ----------
    dx: :class:`float`
        Distance to compute time for.

    start_speed: :class:`.api.Speed`
        Speed at the start (in level header).

    portals: Sequence[:class:`.api.Object`]
        Speed portals in the level, ordered by x position.

    Returns
    -------
    :class:`float`
        Calculated time.
    """
    speed = speed_map.get(start_speed.value)

    if not portals:
        return dx / speed

    last_x = 0
    total = 0

    for portal in portals:
        x = portal.x

        if dx <= x:
            break

        current = x - last_x

        total += current / speed

        speed = speed_map.get(portal.id, speed)

        last_x = x

    return (dx - last_x) / speed + total


def _is_portal(maybe_portal: Object) -> bool:
    return maybe_portal.id in _portals and maybe_portal.is_checked()


def _is_speed_portal(maybe_portal: Object) -> bool:
    return maybe_portal.id in _speed_protals and maybe_portal.is_checked()


def _get_x(some_object: Object) -> Union[float, int]:
    return some_object.x


def _inf_range(start: int = 0, step: int = 1) -> Iterator[int]:
    value = start

    while True:
        yield value
        value += step


def _find_next(
    numbers: Iterable[int], given_range: Optional[Iterable[int]] = None,
) -> Optional[int]:
    if given_range is None:
        given_range = _inf_range(start=1)

    for number in given_range:
        if number not in numbers:
            return number


class Editor:
    """Editor interface of gd.py.

    Editor can be created either by hand, from decoded level's data, or taken from a level itself.
    """

    def __init__(self, *objects: Sequence[Object], **header_args) -> None:
        self.header = Header(**header_args)
        self.objects = list(objects)
        self._set_callback()

    def __json__(self) -> Dict[str, Union[Header, Sequence[Object]]]:
        return dict(header=self.header, objects=self.objects)

    def _set_callback(self, caller: Any = None, attribute: Optional[str] = None) -> None:
        self._callback = caller
        self._attr = attribute

    @classmethod
    def launch(cls, caller: Any, attribute: str) -> Editor:
        return launch_editor(caller, attribute)

    def dump_back(self) -> None:
        dump_editor(self)

    @classmethod
    def from_string(cls, data: Union[bytes, str]) -> Editor:
        if isinstance(data, bytes):
            try:
                data = data.decode()

            except UnicodeDecodeError:
                raise EditorError("Invalid level data received.") from None

        if not data:
            # nothing interesting...
            return cls()

        info, *objects = data.split(";")
        # remove last object if none
        try:
            last = objects.pop()
            if last:
                objects.append(last)
        except IndexError:
            pass

        header = Header.from_string(info)
        objects = list(map(Object.from_string, objects))

        return cls(*objects).set_header(header)

    def __repr__(self) -> str:
        info = {"objects": len(self.objects), "header": "<...>"}
        return make_repr(self, info)

    def __iter__(self) -> Iterable[Object]:
        return iter(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    def set_header(self, header: Header) -> Editor:
        """Set header of Editor instance to ``header``."""
        if isinstance(header, Header):
            self.header = header
        return self

    def get_header(self) -> Header:
        """Get header of Editor instance."""
        return self.header

    def copy_header(self) -> Header:
        """Copy header of Editor instance."""
        return self.header.copy()

    def get_groups(self) -> Iterable[int]:
        """Fetch all used groups in Editor instance and return them as a set."""
        groups = set()

        for obj in self.objects:
            new_groups, group = obj.groups, obj.target_group

            if new_groups is not None:
                groups.update(new_groups)

            if group is not None:
                groups.add(group)

        return groups

    def get_color_ids(self) -> Iterable[int]:
        """Fetch all used color IDs in Editor instance and return them as a set."""
        color_ids = set()

        for obj in self.objects:
            color_1, color_2 = obj.color_1, obj.color_2

            if color_1 is not None:
                color_ids.add(color_1)
            if color_2 is not None:
                color_ids.add(color_2)

        color_ids.update(color.id for color in self.get_colors())

        return color_ids

    def get_free_group(self) -> Optional[int]:
        """Get next free group of Editor instance. ``None`` if not found."""
        return _find_next(self.get_groups())

    def get_free_color_id(self) -> Optional[int]:
        """Get next free color ID of Editor instance. ``None`` if not found."""
        return _find_next(self.get_color_ids())

    def get_portals(self) -> List[Object]:
        """Fetch all portals / speed triggers used in this level, sorted by position in level."""
        return sorted(filter(_is_portal, self.objects), key=(_get_x))

    def get_speed_portals(self) -> List[Object]:
        """Fetch all speed triggers used in this level, sorted by position in level."""
        return sorted(filter(_is_speed_portal, self.objects), key=(_get_x))

    def get_x_length(self) -> Union[float, int]:
        """Get the X position of a last object. Default is 0."""
        return max(map(_get_x, self.objects), default=0)

    def get_speed(self) -> Speed:
        """Get speed from a header, or return normal speed."""
        return self.header.speed or Speed(0)

    def get_length(self, x: Optional[Union[float, int]] = None) -> float:
        """Calculate length of the level in seconds."""
        if x is None:
            x = self.get_x_length()

        portals = self.get_speed_portals()
        speed = self.get_speed()

        return get_length_from_x(x, speed, portals)

    def get_color(self, directive_or_id: Union[int, str]) -> Optional[ColorChannel]:
        """Get color by ID or special directive. ``None`` if not found."""
        return self.header.colors.get(directive_or_id)

    def get_colors(self) -> ColorCollection:
        """Return a reference to colors of the Editor instance."""
        return self.header.colors

    def copy_colors(self) -> ColorCollection:
        """Copy colors of the Editor instance."""
        return self.header.copy_colors()

    def add_colors(
        self, *colors: Sequence[Union[Tuple[int, int, int], int, ColorCollection]]
    ) -> Editor:
        """Add colors to the Editor."""
        self.header.colors.update(colors)
        return self

    def get_objects(self) -> List[Object]:
        """Return a reference to object of the Editor instance."""
        return self.objects

    def add_objects(self, *objects: Sequence[Object]) -> Editor:
        """Add objects to ``self.objects``."""
        self.objects.extend(list(objects))
        return self

    def copy_objects(self) -> List[Object]:
        """Copy objects of the Editor instance."""
        return list(obj.copy() for obj in self.objects)

    def map(self, function: Callable[[Object], Any]) -> map:
        """:class:`map`: Same as calling ``map`` on ``self.objects``."""
        return map(function, self.objects)

    def filter(self, function: Callable[[Object], Any]) -> filter:
        """:class:`filter`: Same as calling ``filter`` on ``self.objects``."""
        return filter(function, self.objects)

    def dump_to_level(self, level: Level, append_sc: bool = True) -> None:
        """Dump ``self`` to a ``level`` object."""
        level.options.update(data=self.dump(append_sc=append_sc))

    def dump_to_api(self, api: LevelAPI, append_sc: bool = True) -> None:
        api.edit(level_string=self.dump(append_sc=append_sc))

    def dump(self, append_sc: bool = True) -> str:
        """Dump all objects and header into a level data string."""
        seq = [self.header.dump(), *(obj.dump() for obj in self.objects)]

        if append_sc:
            seq.append("")

        data = ";".join(map(str, seq))
        return data

    def copy(self) -> Editor:
        """Return a copy of the Editor instance."""
        return Editor(self.copy_header(), *self.copy_objects())


def launch_editor(caller: Any, attribute: str) -> Editor:
    string = getattr(caller, attribute)
    editor = Editor.from_string(string)
    editor._set_callback(caller, attribute)
    return editor


def dump_editor(editor: Editor) -> None:
    if None in (editor._callback, editor._attr):
        return
    string = editor.dump()
    setattr(editor._callback, editor._attr, string)
