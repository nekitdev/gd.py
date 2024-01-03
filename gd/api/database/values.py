from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from typing_aliases import StringDict
from typing_extensions import Self

from gd.api.database.common import ONE, prefix
from gd.api.database.variables import Variables
from gd.robtop_view import StringRobTopView
from gd.string_utils import starts_with

__all__ = ("Values",)

CUBES = "i"
SHIPS = "ship"
BALLS = "ball"
UFOS = "bird"
WAVES = "dart"
ROBOTS = "robot"
SPIDERS = "spider"
# SWINGS = "swing"
EXPLOSIONS = "death"
STREAKS = "special"
COLORS_1 = "c0"
COLORS_2 = "c1"

CUBES_PREFIX = prefix(CUBES)
SHIPS_PREFIX = prefix(SHIPS)
BALLS_PREFIX = prefix(BALLS)
UFOS_PREFIX = prefix(UFOS)
WAVES_PREFIX = prefix(WAVES)
ROBOTS_PREFIX = prefix(ROBOTS)
SPIDERS_PREFIX = prefix(SPIDERS)
# SWINGS_PREFIX = prefix(SWINGS)
EXPLOSIONS_PREFIX = prefix(EXPLOSIONS)
STREAKS_PREFIX = prefix(STREAKS)
COLORS_1_PREFIX = prefix(COLORS_1)
COLORS_2_PREFIX = prefix(COLORS_2)


@define()
class Values:
    variables: Variables = field(factory=Variables)

    cubes: OrderedSet[int] = field(factory=ordered_set)
    ships: OrderedSet[int] = field(factory=ordered_set)
    balls: OrderedSet[int] = field(factory=ordered_set)
    ufos: OrderedSet[int] = field(factory=ordered_set)
    waves: OrderedSet[int] = field(factory=ordered_set)
    robots: OrderedSet[int] = field(factory=ordered_set)
    spiders: OrderedSet[int] = field(factory=ordered_set)
    # swings: OrderedSet[int] = field(factory=ordered_set)
    explosions: OrderedSet[int] = field(factory=ordered_set)
    streaks: OrderedSet[int] = field(factory=ordered_set)
    colors_1: OrderedSet[int] = field(factory=ordered_set)
    colors_2: OrderedSet[int] = field(factory=ordered_set)

    @property
    def prefix_to_ordered_set(self) -> StringDict[OrderedSet[int]]:
        return {
            CUBES_PREFIX: self.cubes,
            SHIPS_PREFIX: self.ships,
            BALLS_PREFIX: self.balls,
            UFOS_PREFIX: self.ufos,
            WAVES_PREFIX: self.waves,
            ROBOTS_PREFIX: self.robots,
            SPIDERS_PREFIX: self.spiders,
            # SWINGS_PREFIX: self.swings,
            EXPLOSIONS_PREFIX: self.explosions,
            STREAKS_PREFIX: self.streaks,
            COLORS_1_PREFIX: self.colors_1,
            COLORS_2_PREFIX: self.colors_2,
        }

    @classmethod
    def from_robtop_view(cls, view: StringRobTopView[str]) -> Self:
        self = cls()

        self.variables = Variables.from_robtop_view(view)

        for prefix, ordered_set in self.prefix_to_ordered_set.items():
            length = len(prefix)

            for name in view.mapping:
                if starts_with(name, prefix):
                    icon_id = int(name[length:])

                    ordered_set.append(icon_id)

        return self

    def to_robtop_data(self) -> StringDict[str]:
        data = self.variables.to_robtop_data()
        one = ONE

        for prefix, ordered_set in self.prefix_to_ordered_set.items():
            for string in iter(ordered_set).map(str).unwrap():
                data[prefix + string] = one

        return data
