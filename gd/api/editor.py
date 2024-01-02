from __future__ import annotations

from operator import attrgetter as get_attribute_factory
from typing import TYPE_CHECKING, Iterable, Iterator, List, Sequence, Set, Union, overload

from attrs import define, field
from iters.iters import iter, wrap_iter
from typing_aliases import is_slice

from gd.api.header import Header
from gd.api.objects import (
    Object,
    StartPosition,
    Trigger,
    has_additional_group,
    has_target_group,
    is_start_position,
    is_trigger,
    migrate_objects,
    object_from_robtop,
    object_to_robtop,
)
from gd.enums import Speed, SpeedChangeType, SpeedMagic
from gd.models_constants import OBJECTS_SEPARATOR
from gd.models_utils import concat_objects, split_objects
from gd.robtop import RobTop

if TYPE_CHECKING:
    from gd.api.color_channels import ColorChannels
    from typing_extensions import Self


__all__ = ("Editor", "time_length")

SPEED_TO_MAGIC = {
    Speed.SLOW: SpeedMagic.SLOW,
    Speed.NORMAL: SpeedMagic.NORMAL,
    Speed.FAST: SpeedMagic.FAST,
    Speed.FASTER: SpeedMagic.FASTER,
    Speed.FASTEST: SpeedMagic.FASTEST,
}

SPEED_CHANGE_TO_MAGIC = {
    SpeedChangeType.SLOW: SpeedMagic.SLOW,
    SpeedChangeType.NORMAL: SpeedMagic.NORMAL,
    SpeedChangeType.FAST: SpeedMagic.FAST,
    SpeedChangeType.FASTER: SpeedMagic.FASTER,
    SpeedChangeType.FASTEST: SpeedMagic.FASTEST,
}


def time_length(
    distance: float,
    start_speed: Speed = Speed.NORMAL,
    speed_changes: Iterable[Object] = (),
) -> float:
    """Computes the time (in seconds) to travel from `0` to `distance`, respecting speed portals.

    Arguments:
        distance: The distance to stop calculating at.
        start_speed: The starting speed (found in the header).
        speed_changes: Speed changes in the level, ordered by `x` position.

    Returns:
        The calculated time (in seconds).
    """
    magic = SPEED_TO_MAGIC[start_speed]

    if not speed_changes:
        return distance / magic

    last_x = 0.0
    total = 0.0

    for speed_change in speed_changes:
        x = speed_change.x

        if x > distance:
            break

        delta = x - last_x

        total += delta / magic

        magic = SPEED_CHANGE_TO_MAGIC[SpeedChangeType(speed_change.id)]

        last_x = x

    delta = distance - last_x

    total += delta / magic

    return total


DEFAULT_START = 1
DEFAULT_NEXT = 0


def find_next(values: Set[int], start: int = DEFAULT_START) -> int:
    for value in iter.count_from(start).unwrap():
        if value not in values:
            return value

    return DEFAULT_NEXT  # pragma: never


DEFAULT_X = 0.0

X = "x"

get_x = get_attribute_factory(X)


@define()
class Editor(Sequence[Object], RobTop):
    """Represents editors."""

    header: Header = field(factory=Header)
    """The header of the editor."""
    objects: List[Object] = field(factory=list)
    """The objects of the editor."""

    @classmethod
    def from_objects(cls, *objects: Object, header: Header) -> Self:
        return cls(header, list(objects))

    @classmethod
    def from_object_iterable(cls, objects: Iterable[Object], header: Header) -> Self:
        return cls(header, list(objects))

    def __len__(self) -> int:
        return len(self.objects)

    @overload
    def __getitem__(self, index: int) -> Object:
        ...

    @overload
    def __getitem__(self, index: slice) -> Self:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Object, Self]:
        if is_slice(index):
            return self.from_object_iterable(self.objects[index], self.header)

        return self.objects[index]  # type: ignore

    @property
    def color_channels(self) -> ColorChannels:
        return self.header.color_channels

    def set_header(self, header: Header) -> Self:
        self.header = header

        return self

    def set_color_channels(self, color_channels: ColorChannels) -> Self:
        self.header.color_channels = color_channels

        return self

    @wrap_iter
    def iter_groups(self) -> Iterator[int]:
        for object in self.objects:
            yield from object.groups

            if has_target_group(object):
                yield object.target_group_id

            if has_additional_group(object):
                yield object.additional_group_id

    @property
    def groups(self) -> Set[int]:
        return self.iter_groups().set()

    @property
    def free_group(self) -> int:
        return find_next(self.groups)

    @wrap_iter
    def iter_color_ids(self) -> Iterator[int]:
        for object in self.objects:
            yield object.base_color_id
            yield object.detail_color_id

        yield from self.color_channels

    @property
    def color_ids(self) -> Set[int]:
        return self.iter_color_ids().set()

    @property
    def free_color_id(self) -> int:
        return find_next(self.color_ids)

    @wrap_iter
    def iter_start_positions(self) -> Iterator[StartPosition]:
        return filter(is_start_position, self.objects)

    @property
    def start_position(self) -> List[StartPosition]:
        return self.iter_start_positions().sorted_by(get_x)

    @wrap_iter
    def iter_portals(self) -> Iterator[Object]:
        return (object for object in self.objects if object.is_portal())

    @property
    def portals(self) -> List[Object]:
        return self.iter_portals().sorted_by(get_x)

    @wrap_iter
    def iter_speed_changes(self) -> Iterator[Object]:
        return (object for object in self.objects if object.is_speed_change())

    @property
    def speed_changes(self) -> List[Object]:
        return self.iter_speed_changes().sorted_by(get_x)

    @wrap_iter
    def iter_triggers(self) -> Iterator[Trigger]:
        return filter(is_trigger, self.objects)

    @property
    def triggers(self) -> List[Trigger]:
        return self.iter_triggers().sorted_by(get_x)

    @property
    def x_length(self) -> float:
        return iter(self.objects).map(get_x).max().unwrap_or(DEFAULT_X)

    @property
    def start_speed(self) -> Speed:
        return self.header.speed

    @property
    def length(self) -> float:
        return time_length(self.x_length, self.start_speed, self.speed_changes)

    @classmethod
    def from_robtop(cls, string: str) -> Self:
        iterator = iter(split_objects(string)).filter(None)

        header_option = iterator.next().extract()

        if header_option is None:
            header = Header()

        else:
            header = Header.from_robtop(header_option)

        objects = iterator.map(object_from_robtop).collect_iter(migrate_objects).list()

        return cls(header, objects)

    def to_robtop(self) -> str:
        return (
            iter(self.objects)
            .map(object_to_robtop)
            .prepend(self.header.to_robtop())
            .collect(concat_objects)
        )

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return OBJECTS_SEPARATOR in string
