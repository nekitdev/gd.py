from .._typing import (
    Any,
    Callable,
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

from .enums import (
    SpeedMagic,
    Speed,
    PortalType,
)
from .struct import (
    Object,
    ColorChannel,
    Header,
    ColorCollection,
    LevelAPI
)

from ..errors import EditorError
from ..utils.text_tools import make_repr

__all__ = ('Editor', 'get_length_from_x')

speed_map = {}

for s in ('slow', 'normal', 'fast', 'faster', 'fastest'):
    a, b, c = (
        SpeedMagic[s.upper()],
        Speed[s.upper()],
        PortalType[s.title() + 'Speed']
    )
    speed_map.update({b.value: a.value, c.value: a.value})

_portals = {enum.value for enum in PortalType}
_speed_protals = {enum.value for enum in PortalType if ('speed' in enum.name.lower())}


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


def _is_portal(obj: Object) -> bool:
    return obj.id in _portals and obj.is_checked()


def _is_speed_portal(obj: Object) -> bool:
    return obj.id in _speed_protals and obj.is_checked()


def _get_x(obj: Object) -> Union[float, int]:
    return obj.x


def _inf_range(start: int = 0, step: int = 1) -> Iterator[int]:
    value = start

    while True:
        yield value
        value += step


def _find_next(s: Iterable[int], rng: Optional[Iterable[int]] = None) -> Optional[int]:
    if rng is None:
        rng = _inf_range()
    for i in rng:
        if i not in s:
            return i


class Editor:
    """Editor interface of gd.py.

    Editor can be created either by hand, from decoded level's data, or taken from a level itself.
    """
    def __init__(self, header: Header = None, *objects: Sequence[Object]) -> None:
        self.header = header or Header()
        self.objects = list(objects)
        self._set_callback()

    def __json__(self) -> dict:
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
                raise EditorError('Invalid level data recieved.') from None

        if not data:
            # nothing interesting...
            return cls()

        info, *objects = data.split(';')
        # remove last object if none
        try:
            last = objects.pop()
            if last:
                objects.append(last)
        except IndexError:
            pass

        header = Header.from_string(info)
        objects = list(map(Object.from_string, objects))

        return cls(header, *objects)

    def __repr__(self) -> str:
        info = {
            'len': len(self.objects),
            'objects': '[...]'
        }
        return make_repr(self, info)

    def __iter__(self) -> Iterable[Object]:
        return iter(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    def set_header(self, header: Header) -> None:
        if isinstance(header, Header):
            self.header = header

    def get_header(self) -> Header:
        return self.header

    def copy_header(self) -> Header:
        return self.header.copy()

    def get_groups(self) -> Iterable[int]:
        groups = set()

        for obj in self.objects:
            g = obj.groups or set()
            groups.update(g)

        return groups

    def get_color_ids(self) -> Iterable[int]:
        color_ids = set()

        for obj in self.objects:
            color_ids.update((obj.color_1, obj.color_2))

        color_ids.discard(None)

        return color_ids

    def get_free_group(self) -> Optional[int]:
        return _find_next(self.get_groups())

    def get_free_color_id(self) -> Optional[int]:
        return _find_next(self.get_color_ids())

    def get_portals(self) -> List[Object]:
        return sorted(filter(_is_portal, self.objects), key=(_get_x))

    def get_speed_portals(self) -> List[Object]:
        return sorted(filter(_is_speed_portal, self.objects), key=(_get_x))

    def get_x_length(self) -> Union[float, int]:
        return max(map(_get_x, self.objects), default=0)

    def get_speed(self) -> Speed:
        return self.header.speed or Speed(0)

    def get_length(self, x: Optional[Union[float, int]] = None) -> float:
        if x is None:
            x = self.get_x_length()

        portals = self.get_speed_portals()
        speed = self.get_speed()

        return get_length_from_x(x, speed, portals)

    def get_color(self, directive_or_id: Union[int, str]) -> ColorChannel:
        return self.header.colors.get(directive_or_id)

    def get_colors(self) -> ColorCollection:
        return self.header.colors

    def copy_colors(self) -> ColorCollection:
        return self.header.copy_colors()

    def add_colors(
        self, *colors: Sequence[Union[Tuple[int, int, int], int, ColorCollection]]
    ) -> None:
        self.header.colors.update(colors)

    def get_objects(self) -> List[Object]:
        return self.objects

    def add_objects(self, *objects: Sequence[Object]) -> None:
        """Add objects to ``self.objects``."""
        self.objects.extend(list(objects))

    def copy_objects(self) -> List[Object]:
        """List[:class:`.api.Object`]: Copy objects of ``self``.
        Note: copies, not references are returned!
        """
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
            seq.append(str())

        data = ';'.join(map(str, seq))
        return data

    def copy(self) -> Editor:
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
