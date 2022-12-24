from functools import partial
from operator import attrgetter as get_attribute_factory
from typing import Iterable, Iterator, List, Sequence, Set, Type, TypeVar, Union, overload

from attrs import define, field
from iters import iter

from gd.api.color_channels import ColorChannels
from gd.api.header import Header
from gd.api.objects import (
    Object,
    Trigger,
    has_additional_group,
    has_target_group,
    is_trigger,
    object_from_binary,
    object_from_robtop,
    object_to_binary,
    object_to_robtop,
)
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder, Speed, SpeedChangeType, SpeedMagic
from gd.models_constants import OBJECTS_SEPARATOR
from gd.models_utils import concat_objects, split_objects
from gd.robtop import RobTop
from gd.typing import is_instance

__all__ = ("Editor", "get_time_length")

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


def get_time_length(
    distance: float,
    start_speed: Speed = Speed.NORMAL,
    speed_changes: Iterable[Object] = (),
) -> float:
    """Computes the time (in seconds) to travel from `0` to `distance`, respecting speed portals.

    Parameters:
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
    for value in iter.count().unwrap():
        if value not in values:
            return value

    return DEFAULT_NEXT  # pragma: never


DEFAULT_X = 0.0

X = "x"

get_x = get_attribute_factory(X)

E = TypeVar("E", bound="Editor")


@define()
class Editor(RobTop, Binary, Sequence[Object]):
    header: Header = field(factory=Header)
    objects: List[Object] = field(factory=list)

    @classmethod
    def from_objects(cls: Type[E], *objects: Object, header: Header) -> E:
        return cls(header, list(objects))

    # callback?

    @classmethod
    def from_object_iterable(cls: Type[E], objects: Iterable[Object], header: Header) -> E:
        return cls(header, list(objects))

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

    @property
    def color_channels(self) -> ColorChannels:
        return self.header.color_channels

    def set_header(self: E, header: Header) -> E:
        self.header = header

        return self

    def set_color_channels(self: E, color_channels: ColorChannels) -> E:
        self.header.color_channels = color_channels

        return self

    def iter_groups(self) -> Iterator[int]:
        for object in self.objects:
            yield from object.groups

            if has_target_group(object):
                yield object.target_group_id

            if has_additional_group(object):
                yield object.additional_group_id

    @property
    def groups(self) -> Set[int]:
        return set(self.iter_groups())

    @property
    def free_group(self) -> int:
        return find_next(self.groups)

    def iter_color_ids(self) -> Iterator[int]:
        for editor_object in self.objects:
            yield editor_object.base_color_id
            yield editor_object.detail_color_id

        yield from self.color_channels

    @property
    def color_ids(self) -> Set[int]:
        return set(self.iter_color_ids())

    @property
    def free_color_id(self) -> int:
        return find_next(self.color_ids)

    def iter_portals(self) -> Iterator[Object]:
        for object in self.objects:
            if object.is_portal():
                yield object

    @property
    def portals(self) -> List[Object]:
        return sorted(self.iter_portals(), key=get_x)

    def iter_speed_changes(self) -> Iterator[Object]:
        for object in self.objects:
            if object.is_speed_change():
                yield object

    @property
    def speed_changes(self) -> List[Object]:
        return sorted(self.iter_speed_changes(), key=get_x)

    def iter_triggers(self) -> Iterator[Trigger]:
        for object in self.objects:
            if is_trigger(object):
                yield object

    @property
    def triggers(self) -> List[Trigger]:
        return sorted(self.iter_triggers(), key=get_x)

    @property
    def x_length(self) -> float:
        return iter(self.objects).map(get_x).max_or(DEFAULT_X)

    @property
    def start_speed(self) -> Speed:
        return self.header.speed

    @property
    def length(self) -> float:
        return get_time_length(self.x_length, self.start_speed, self.speed_changes)

    @classmethod
    def from_binary(
        cls: Type[E],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> E:
        header = Header.from_binary(binary, order, version)

        reader = Reader(binary)

        iterable_length = reader.read_u32(order)

        object_from_binary_function = partial(object_from_binary, binary, order, version)

        iterable = iter.repeat_exactly_with(object_from_binary_function, iterable_length).unwrap()

        return cls.from_object_iterable(iterable, header)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        self.header.to_binary(binary, order, version)

        writer = Writer(binary)

        objects = self.objects

        writer.write_u32(len(objects), order)

        for object in objects:
            object_to_binary(object, binary, order, version)

    @classmethod
    def from_robtop(cls: Type[E], string: str) -> E:
        iterator = iter(split_objects(string)).filter(None)

        header_string = iterator.next_or_none()

        if header_string is None:
            header = Header()

        else:
            header = Header.from_robtop(header_string)

        objects = iterator.map(object_from_robtop).list()

        return cls(header, objects)

    def to_robtop(self) -> str:
        iterator = iter(self.objects).map(object_to_robtop).prepend(self.header.to_robtop())

        return concat_objects(iterator.unwrap())

    @classmethod
    def can_be_in(cls, string: str) -> bool:
        return OBJECTS_SEPARATOR in string


DEFAULT_DATA = Editor().to_bytes()
