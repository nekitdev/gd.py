from typing import Type, TypeVar

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from typing_aliases import StringDict, StringMapping

from gd.api.database.common import (
    DEMON,
    GAUNTLET,
    GAUNTLET_DEMON,
    GAUNTLET_STAR,
    MAP_PACK,
    NORMAL,
    OFFICIAL,
    ONE,
    STAR,
    TIMELY,
    TIMELY_DEMON,
    TIMELY_STAR,
    prefix,
)
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.constants import WEEKLY_ID_ADD
from gd.enums import ByteOrder

__all__ = ("Completed",)


@define()
class CompletedPair:
    levels: OrderedSet[int] = field(factory=ordered_set)
    demons: OrderedSet[int] = field(factory=ordered_set)


@define()
class Stars:
    normal: OrderedSet[int] = field(factory=ordered_set)
    daily: OrderedSet[int] = field(factory=ordered_set)
    weekly: OrderedSet[int] = field(factory=ordered_set)
    gauntlet: OrderedSet[int] = field(factory=ordered_set)


OFFICIAL_PREFIX = prefix(OFFICIAL)
NORMAL_PREFIX = prefix(NORMAL)
DEMON_PREFIX = prefix(DEMON)
STAR_PREFIX = prefix(STAR)
TIMELY_PREFIX = prefix(TIMELY)
TIMELY_DEMON_PREFIX = prefix(TIMELY_DEMON)
TIMELY_STAR_PREFIX = prefix(TIMELY_STAR)
GAUNTLET_PREFIX = prefix(GAUNTLET)
GAUNTLET_DEMON_PREFIX = prefix(GAUNTLET_DEMON)
GAUNTLET_STAR_PREFIX = prefix(GAUNTLET_STAR)
MAP_PACK_PREFIX = prefix(MAP_PACK)

C = TypeVar("C", bound="Completed")


@define()
class Completed(Binary):
    """Represents completed levels in the database."""

    official: OrderedSet[int] = field(factory=ordered_set)
    normal: CompletedPair = field(factory=CompletedPair)
    timely: CompletedPair = field(factory=CompletedPair)
    gauntlet: CompletedPair = field(factory=CompletedPair)
    map_packs: OrderedSet[int] = field(factory=ordered_set)
    stars: Stars = field(factory=Stars)

    @classmethod
    def from_binary(
        cls: Type[C],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> C:
        reader = Reader(binary, order)

        official_length = reader.read_u8()

        official = iter.repeat_exactly_with(reader.read_u16, official_length).ordered_set()

        normal_levels_length = reader.read_u32()

        normal_levels = iter.repeat_exactly_with(
            reader.read_u32, normal_levels_length
        ).ordered_set()

        normal_demons_length = reader.read_u16()

        normal_demons = iter.repeat_exactly_with(
            reader.read_u32, normal_demons_length
        ).ordered_set()

        normal = CompletedPair(normal_levels, normal_demons)

        timely_levels_length = reader.read_u16()

        timely_levels = iter.repeat_exactly_with(
            reader.read_u32, timely_levels_length  # literally why would level ID be here
        ).ordered_set()

        timely_demons_length = reader.read_u16()

        timely_demons = iter.repeat_exactly_with(
            reader.read_u16, timely_demons_length  # while here we have timely ID
        ).ordered_set()

        timely = CompletedPair(timely_levels, timely_demons)

        gauntlet_levels_length = reader.read_u16()

        gauntlet_levels = iter.repeat_exactly_with(
            reader.read_u32, gauntlet_levels_length
        ).ordered_set()

        gauntlet_demons_length = reader.read_u16()

        gauntlet_demons = iter.repeat_exactly_with(
            reader.read_u32, gauntlet_demons_length
        ).ordered_set()

        gauntlet = CompletedPair(gauntlet_levels, gauntlet_demons)

        map_packs_length = reader.read_u16()

        map_packs = iter.repeat_exactly_with(reader.read_u16, map_packs_length).ordered_set()

        normal_stars_length = reader.read_u32()

        normal_stars = iter.repeat_exactly_with(reader.read_u32, normal_stars_length).ordered_set()

        daily_stars_length = reader.read_u16()

        daily_stars = iter.repeat_exactly_with(reader.read_u16, daily_stars_length).ordered_set()

        weekly_stars_length = reader.read_u16()

        weekly_stars = iter.repeat_exactly_with(reader.read_u16, weekly_stars_length).ordered_set()

        gauntlet_stars_length = reader.read_u16()

        gauntlet_stars = iter.repeat_exactly_with(
            reader.read_u32, gauntlet_stars_length
        ).ordered_set()

        stars = Stars(normal_stars, daily_stars, weekly_stars, gauntlet_stars)

        return cls(
            official=official,
            normal=normal,
            timely=timely,
            gauntlet=gauntlet,
            map_packs=map_packs,
            stars=stars,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        official = self.official

        writer.write_u8(len(official))

        iter(official).for_each(writer.write_u16)

        normal = self.normal

        normal_levels = normal.levels

        writer.write_u32(len(normal_levels))

        iter(normal_levels).for_each(writer.write_u32)

        normal_demons = normal.demons

        writer.write_u16(len(normal_demons))

        iter(normal_demons).for_each(writer.write_u32)

        timely = self.timely

        timely_levels = timely.levels

        writer.write_u16(len(timely_levels))

        iter(timely_levels).for_each(writer.write_u32)

        timely_demons = timely.demons

        writer.write_u16(len(timely_demons))

        iter(timely_demons).for_each(writer.write_u16)

        gauntlet = self.gauntlet

        gauntlet_levels = gauntlet.levels

        writer.write_u16(len(gauntlet_levels))

        iter(gauntlet_levels).for_each(writer.write_u32)

        gauntlet_demons = gauntlet.demons

        writer.write_u16(len(gauntlet_demons))

        iter(gauntlet_demons).for_each(writer.write_u32)

        map_packs = self.map_packs

        writer.write_u16(len(map_packs))

        iter(map_packs).for_each(writer.write_u16)

        stars = self.stars

        normal_stars = stars.normal

        writer.write_u32(len(normal_stars))

        iter(normal_stars).for_each(writer.write_u32)

        daily_stars = stars.daily

        writer.write_u16(len(daily_stars))

        iter(daily_stars).for_each(writer.write_u16)

        weekly_stars = stars.weekly

        writer.write_u16(len(weekly_stars))

        iter(weekly_stars).for_each(writer.write_u16)

        gauntlet_stars = stars.gauntlet

        writer.write_u16(len(gauntlet_stars))

        iter(gauntlet_stars).for_each(writer.write_u32)

    @classmethod
    def from_robtop_data(cls: Type[C], data: StringMapping[str]) -> C:  # type: ignore
        self = cls()

        normal = self.normal
        timely = self.timely
        gauntlet = self.gauntlet
        stars = self.stars

        prefix_to_ordered_set = {
            OFFICIAL_PREFIX: self.official,
            NORMAL_PREFIX: normal.levels,
            DEMON_PREFIX: normal.demons,
            TIMELY_PREFIX: timely.levels,
            GAUNTLET_PREFIX: gauntlet.levels,
            GAUNTLET_DEMON_PREFIX: gauntlet.demons,
            MAP_PACK_PREFIX: self.map_packs,
            STAR_PREFIX: stars.normal,
            GAUNTLET_STAR_PREFIX: stars.gauntlet,
        }

        for prefix, ordered_set in prefix_to_ordered_set.items():
            length = len(prefix)

            for name in data.keys():
                if name.startswith(prefix):
                    ordered_set.add(int(name[length:]))

        weekly_id_add = WEEKLY_ID_ADD

        # special handling for timely demons (weeklies)

        timely_demons = timely.demons

        prefix = TIMELY_DEMON_PREFIX
        length = len(prefix)

        for name in data.keys():
            if name.startswith(prefix):
                timely_id = int(name[length:])

                result, timely_id = divmod(timely_id, weekly_id_add)

                if result:
                    timely_demons.add(timely_id)

        # special handling for timely stars

        daily_stars = stars.daily
        weekly_stars = stars.weekly

        prefix = TIMELY_STAR_PREFIX
        length = len(prefix)

        for name in data.keys():
            if name.startswith(prefix):
                timely_id = int(name[length:])

                result, timely_id = divmod(timely_id, weekly_id_add)

                if result:
                    weekly_stars.add(timely_id)

                else:
                    daily_stars.add(timely_id)

        return self

    def to_robtop_data(self) -> StringDict[str]:
        data: StringDict[str] = {}
        one = ONE

        official = self.official
        official_prefix = OFFICIAL_PREFIX

        official_data = {official_prefix + str(level_id): one for level_id in official}

        data.update(official_data)

        normal = self.normal

        normal_levels = normal.levels
        normal_prefix = NORMAL_PREFIX

        normal_levels_data = {normal_prefix + str(level_id): one for level_id in normal_levels}

        data.update(normal_levels_data)

        normal_demons = normal.demons
        normal_demons_prefix = DEMON_PREFIX

        normal_demons_data = {
            normal_demons_prefix + str(level_id): one for level_id in normal_demons
        }

        data.update(normal_demons_data)

        timely = self.timely

        timely_levels = timely.levels
        timely_levels_prefix = TIMELY_PREFIX

        timely_levels_data = {
            timely_levels_prefix + str(level_id): one for level_id in timely_levels
        }

        data.update(timely_levels_data)

        weekly_id_add = WEEKLY_ID_ADD

        timely_demons = timely.demons
        timely_demons_prefix = TIMELY_DEMON_PREFIX

        timely_demons_data = {
            timely_demons_prefix + str(weekly_id + weekly_id_add): one
            for weekly_id in timely_demons
        }

        data.update(timely_demons_data)

        gauntlet = self.gauntlet

        gauntlet_levels = gauntlet.levels
        gauntlet_levels_prefix = GAUNTLET_PREFIX

        gauntlet_levels_data = {
            gauntlet_levels_prefix + str(level_id): one for level_id in gauntlet_levels
        }

        data.update(gauntlet_levels_data)

        gauntlet_demons = gauntlet.demons
        gauntlet_demons_prefix = GAUNTLET_DEMON_PREFIX

        gauntlet_demons_data = {
            gauntlet_demons_prefix + str(level_id): one for level_id in gauntlet_demons
        }

        data.update(gauntlet_demons_data)

        map_packs = self.map_packs
        map_packs_prefix = MAP_PACK_PREFIX

        map_packs_data = {map_packs_prefix + str(map_pack_id): one for map_pack_id in map_packs}

        data.update(map_packs_data)

        stars = self.stars

        normal_stars = stars.normal
        normal_stars_prefix = STAR_PREFIX

        normal_stars_data = {normal_stars_prefix + str(level_id): one for level_id in normal_stars}

        data.update(normal_stars_data)

        timely_stars_prefix = TIMELY_STAR_PREFIX

        daily_stars = stars.daily

        daily_stars_data = {timely_stars_prefix + str(daily_id): one for daily_id in daily_stars}

        data.update(daily_stars_data)

        weekly_stars = stars.weekly

        weekly_stars_data = {
            timely_stars_prefix + str(weekly_id + weekly_id_add): one for weekly_id in weekly_stars
        }

        data.update(weekly_stars_data)

        gauntlet_stars = stars.gauntlet
        gauntlet_stars_prefix = GAUNTLET_STAR_PREFIX

        gauntlet_stars_data = {
            gauntlet_stars_prefix + str(level_id): one for level_id in gauntlet_stars
        }

        data.update(gauntlet_stars_data)

        return data
