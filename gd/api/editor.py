from itertools import count
from operator import attrgetter

from gd.enums import Speed
from gd.errors import EditorError
from gd.text_utils import make_repr
from gd.typing import Dict, Iterable, Iterator, List, Optional, Set, Union, TYPE_CHECKING

from gd.api.struct import (  # type: ignore
    SPEEDS,
    Object,
    ColorChannel,
    Header,
    ColorCollection,
    LevelAPI,
)

__all__ = ("Editor", "get_time_length")

if TYPE_CHECKING:
    from gd.level import Level  # noqa


def get_time_length(
    dx: float, start: Speed = Speed.NORMAL, speed_changes: Iterable[Object] = (),  # type: ignore
) -> float:
    """Compute the time (in seconds) to travel from ``x1`` to ``x2`` on x axis,
    respecting speed portals.

    Parameters
    ----------
    dx: :class:`float`
        Distance to stop calculating at.

    start: :class:`.api.Speed`
        Speed at the start (from the level header).

    speed_changes: Iterable[:class:`.api.Object`]
        Speed changes in the level, ordered by x position.

    Returns
    -------
    :class:`float`
        Calculated time (seconds).
    """
    speed = SPEEDS[start.value]

    if not speed_changes:
        return dx / speed

    last_x = 0.0
    total = 0.0

    for speed_change in speed_changes:
        x = speed_change.x

        if x > dx:
            break

        segment = x - last_x

        total += segment / speed

        speed = SPEEDS[speed_change.id]

        last_x = x

    return (dx - last_x) / speed + total


def find_next(
    numbers: Iterable[int], number_range: Optional[Iterable[int]] = None,
) -> Optional[int]:
    if number_range is None:
        number_range = count(1)

    for number in number_range:
        if number not in numbers:
            return number

    return None


get_x = attrgetter("x")


class Editor:
    """Editor interface of gd.py.

    Editor can be created either by hand, from decoded level's data, or taken from a level itself.
    """

    def __init__(self, *objects: Object, **header_args) -> None:
        self.header = Header(**header_args)
        self.objects = list(objects)
        self._set_callback()

    def __json__(self) -> Dict[str, Union[Header, List[Object]]]:
        return dict(header=self.header, objects=self.objects)

    def _set_callback(
        self,
        callback: Optional[Union["Level", LevelAPI]] = None,  # type: ignore
        attribute: Optional[str] = None,
    ) -> None:
        self._callback = callback
        self._attribute = attribute

    def dump_back(self) -> None:
        if self._callback is None or self._attribute is None:
            return

        setattr(self._callback, self._attribute, self.to_string())

    @classmethod
    def load_from(
        cls, callback: Union["Level", LevelAPI], attribute: str  # type: ignore
    ) -> "Editor":
        self = cls.from_string(getattr(callback, attribute))

        self._set_callback(callback, attribute)

        return self

    @classmethod
    def from_object_iterable(cls, objects: Iterable[Object], **header_args) -> "Editor":
        self = cls(**header_args)
        self.objects = list(objects)
        return self

    @classmethod
    def from_string(cls, data: Union[bytes, str]) -> "Editor":
        if isinstance(data, bytes):
            try:
                data = data.decode()

            except UnicodeDecodeError:
                raise EditorError("Invalid level data received. Can not decode.") from None

        if not data:
            return cls()

        header_data, *objects_data = filter(bool, data.split(";"))

        header = Header.from_string(header_data)
        objects_iter = map(Object.from_string, objects_data)

        return cls.from_object_iterable(objects_iter).set_header(header)

    def __repr__(self) -> str:
        info = {"object_count": len(self.objects), "header": "<...>"}
        return make_repr(self, info)

    def __len__(self) -> int:
        return len(self.objects)

    def __getitem__(self, item: Union[int, slice]) -> Object:
        return self.objects[item]

    def set_header(self, header: Header) -> "Editor":
        """Set header of Editor instance to ``header``."""
        self.header = header
        return self

    def get_header(self) -> Header:
        """Get header of Editor instance."""
        return self.header

    def copy_header(self) -> Header:
        """Copy header of Editor instance."""
        return self.header.copy()

    def clone_header(self) -> Header:
        """Clone header of Editor instance."""
        return self.header.clone()

    def get_groups(self) -> Set[int]:
        """Fetch all used groups in Editor instance and return them as a set."""
        groups = set()

        for editor_object in self.objects:
            new_groups = editor_object.groups

            if new_groups is not None:
                groups.update(new_groups)

            group = editor_object.target_group

            if group is not None:
                groups.add(group)

        return groups

    def get_color_ids(self) -> Iterable[int]:
        """Fetch all used color IDs in Editor instance and return them as a set."""
        color_ids = set()

        for editor_object in self.objects:
            color_1 = editor_object.color_1

            if color_1 is not None:
                color_ids.add(color_1)

            color_2 = editor_object.color_2

            if color_2 is not None:
                color_ids.add(color_2)

        color_ids.update(color.id for color in self.get_colors())

        return color_ids

    def get_free_group(self) -> Optional[int]:
        """Get next free group of Editor instance. ``None`` if not found."""
        return find_next(self.get_groups())

    def get_free_color_id(self) -> Optional[int]:
        """Get next free color ID of Editor instance. ``None`` if not found."""
        return find_next(self.get_color_ids())

    def get_portals(self) -> List[Object]:
        """Fetch all portals / speed triggers used in this level, sorted by position in level."""
        return sorted(filter(Object.is_portal, self.objects), key=get_x)

    def get_speeds(self) -> List[Object]:
        """Fetch all speed changes used in this level, sorted by position in level."""
        return sorted(filter(Object.is_speed, self.objects), key=get_x)

    def get_x_length(self) -> float:
        """Get the X position of a last object. Default is 0."""
        return max(map(get_x, self.objects), default=0)

    def get_start_speed(self) -> Speed:
        """Get speed from a header, or return normal speed."""
        speed = self.header.speed
        return Speed.NORMAL if speed is None else speed

    def get_length(self, dx: Optional[float] = None) -> float:
        """Calculate length of the level in seconds."""
        if dx is None:
            dx = self.get_x_length()

        return get_time_length(dx, self.get_start_speed(), self.get_speeds())

    def get_color(self, directive_or_id: Union[int, str]) -> Optional[ColorChannel]:
        """Get color by ID or special directive. ``None`` if not found."""
        return self.header.colors.get(directive_or_id)

    def get_colors(self) -> ColorCollection:
        """Return a reference to colors of the Editor instance."""
        return self.header.colors

    def set_colors(self, colors: ColorCollection) -> "Editor":
        self.header.colors = colors
        return self

    colors = property(get_colors, set_colors)  # type: ignore

    def copy_colors(self) -> ColorCollection:
        """Copy colors of the Editor instance."""
        return self.header.colors.copy()

    def clone_colors(self) -> ColorCollection:
        return self.header.colors.clone()

    def add_colors(self, *colors: ColorChannel) -> "Editor":
        """Add colors to the Editor."""
        self.header.colors.update(colors)
        return self

    def remove_colors(self, *colors: ColorChannel) -> "Editor":
        self.header.colors.remove(colors)
        return self

    def get_objects(self) -> List[Object]:
        """Return a reference to object of the Editor instance."""
        return self.objects

    def set_objects(self, objects: List[Object]) -> "Editor":
        self.objects = objects
        return self

    def add_objects(self, *objects: Object) -> "Editor":
        """Add objects to ``self.objects``."""
        self.objects.extend(objects)
        return self

    def remove_objects(self, *objects: Object) -> "Editor":
        objects_to_remove = set(objects)

        self.objects = [
            editor_object
            for editor_object in self.objects
            if editor_object not in objects_to_remove
        ]

        return self

    def copy_objects(self) -> List[Object]:
        """Copy objects of the Editor instance."""
        return [editor_object.copy() for editor_object in self.objects]

    def clone_objects(self) -> List[Object]:
        """Clone objects of the Editor instance."""
        return [editor_object.clone() for editor_object in self.objects]

    def to_string(self, delim: str = ";") -> str:
        """Dump all objects and header into a level data string."""
        return delim.join(self.iter_to_string())

    dump = to_string

    def iter_to_string(self) -> Iterator[str]:
        yield self.header.to_string()

        for editor_object in self.objects:
            yield editor_object.to_string()

    def copy(self) -> "Editor":
        """Return a copy of the Editor instance."""
        cls = self.__class__
        return cls.from_object_iterable(self.copy_objects()).set_header(self.copy_header())

    def clone(self) -> "Editor":
        """Return a clone of the Editor instance."""
        cls = self.__class__
        return cls.from_object_iterable(self.clone_objects()).set_header(self.clone_header())
