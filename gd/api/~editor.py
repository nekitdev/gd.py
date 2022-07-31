from itertools import count
from operator import attrgetter as get_attribute_factory
from typing import TYPE_CHECKING, AbstractSet, Sequence, Set, Type, TypeVar, overload

from attrs import define, field

from gd.api.header import Header
from gd.api.objects import Object, has_target_group
from gd.enums import Speed
from gd.errors import EditorError

__all__ = ("Editor", "get_time_length")

if TYPE_CHECKING:
    from gd.level import Level  # noqa
    from gd.memory.struct import GameLevel  # type: ignore  # noqa


def get_time_length(
    distance: float,
    start: Speed = Speed.NORMAL,  # type: ignore
    speed_changes: Iterable[Object] = (),
) -> float:
    """Compute the time (in seconds) to travel
    from ``0`` to ``distance``, respecting speed portals.

    Parameters
    ----------
    distance: :class:`float`
        Distance to stop calculating at.

    start: :class:`~gd.api.Speed`
        Speed at the start (from the level header).

    speed_changes: Iterable[:class:`~gd.api.Object`]
        Speed changes in the level, ordered by x position.

    Returns
    -------
    :class:`float`
        Calculated time (in seconds).
    """
    speed = SPEEDS[start.value]

    if not speed_changes:
        return distance / speed

    last_x = 0.0
    total = 0.0

    for speed_change in speed_changes:
        x = speed_change.x

        if x > distance:
            break

        delta = x - last_x

        total += delta / speed

        speed = SPEEDS[speed_change.id]

        last_x = x

    delta = distance - last_x

    total += delta / speed

    return total


DEFAULT_START = 1


def find_next(
    values: AbstractSet[int],
    start: int = DEFAULT_START,
) -> int:
    for value in count(start):
        if value not in values:
            return value


X = "x"

get_x = get_attribute_factory(X)

E = TypeVar("E", bound="Editor")


@define()
class Editor(Sequence[Object]):
    header: Header = field(factory=Header)
    objects: List[Object] = field(factory=list)

    @classmethod
    def from_objects(cls: Type[E], *objects: Object, header: Header) -> E:
        return cls(header, list(objects))

    # callback

    @classmethod
    def from_object_iterable(cls: Type[E], objects: Iterable[Object], header: Header) -> E:
        return cls(header, list(objects))

    @classmethod
    def from_string(cls: Type[E], string: str) -> E:
        ...

    def __len__(self) -> int:
        return len(self.objects)

    @overload
    def __getitem__(self, index: int) -> Object:
        ...

    @overload
    def __getitem__(self: E, index: slice) -> E:
        ...

    def __getitem__(self: E, index: Union[int, slice]) -> Union[Object, E]:
        if is_instance(index, int):
            return self.objects[index]

        return self.from_object_iterable(self.objects[index], self.header)

    def set_header(self: E, header: Header) -> E:
        self.header = header

        return self

    def iter_groups(self) -> Iterator[int]:
        for object in self.objects:
            yield from object.groups

            if has_target_group(object):
                yield object.target_group_id

    @property
    def groups(self) -> Set[int]:
        return set(self.iter_groups())

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
        """Set colors of the Editor instance to ``colors``."""
        self.header.colors = colors
        return self

    colors = property(get_colors, set_colors)  # type: ignore

    def copy_colors(self) -> ColorCollection:
        """Copy colors of the Editor instance."""
        return self.header.colors.copy()

    def clone_colors(self) -> ColorCollection:
        """Clone colors of the Editor instance."""
        return self.header.colors.clone()

    def add_colors(self, *colors: ColorChannel) -> "Editor":
        """Add colors to the Editor."""
        self.header.colors.update(colors)
        return self

    def remove_colors(self, *colors: ColorChannel) -> "Editor":
        """Remove colors from the Editor."""
        self.header.colors.remove(colors)
        return self

    def get_objects(self) -> List[Object]:
        """Return a reference to object of the Editor instance."""
        return self.objects

    def set_objects(self, objects: List[Object]) -> "Editor":
        """Set objects of the Editor instance to ``objects``."""
        self.objects = objects
        return self

    def add_objects(self, *objects: Object) -> "Editor":
        """Add objects to ``self.objects``."""
        self.objects.extend(objects)
        return self

    def remove_objects(self, *objects: Object) -> "Editor":
        """Remove objects from the Editor instance."""
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
        return self.from_object_iterable(self.copy_objects()).set_header(self.copy_header())

    def clone(self) -> "Editor":
        """Return a clone of the Editor instance."""
        return self.from_object_iterable(self.clone_objects()).set_header(self.clone_header())
