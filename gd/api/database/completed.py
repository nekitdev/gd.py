from attrs import define, field
from iters.ordered_set import OrderedSet, ordered_set
from typing_aliases import StringDict
from typing_extensions import Self

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
from gd.constants import WEEKLY_ID_ADD
from gd.robtop_view import StringRobTopView
from gd.string_utils import starts_with

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


@define()
class Completed:
    """Represents completed levels in the database."""

    official: OrderedSet[int] = field(factory=ordered_set)
    normal: CompletedPair = field(factory=CompletedPair)
    timely: CompletedPair = field(factory=CompletedPair)
    gauntlet: CompletedPair = field(factory=CompletedPair)
    map_packs: OrderedSet[int] = field(factory=ordered_set)
    stars: Stars = field(factory=Stars)

    @classmethod
    def from_robtop_view(cls, view: StringRobTopView[str]) -> Self:
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

            for name in view.mapping:
                if starts_with(name, prefix):
                    ordered_set.add(int(name[length:]))

        weekly_id_add = WEEKLY_ID_ADD

        # special handling for timely demons (weeklies)

        timely_demons = timely.demons

        prefix = TIMELY_DEMON_PREFIX
        length = len(prefix)

        for name in view.mapping:
            if starts_with(name, prefix):
                timely_id = int(name[length:])

                result, timely_id = divmod(timely_id, weekly_id_add)

                if result:
                    timely_demons.add(timely_id)

        # special handling for timely stars

        daily_stars = stars.daily
        weekly_stars = stars.weekly

        prefix = TIMELY_STAR_PREFIX
        length = len(prefix)

        for name in view.mapping:
            if starts_with(name, prefix):
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
