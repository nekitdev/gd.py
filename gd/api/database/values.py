from typing import Type, TypeVar

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from typing_aliases import StringDict, StringMapping

from gd.api.database.common import ONE, prefix
from gd.api.database.variables import Variables
from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder
from gd.string_utils import starts_with

__all__ = ("Values",)

CUBES = "i"
SHIPS = "ship"
BALLS = "ball"
UFOS = "bird"
WAVES = "dart"
ROBOTS = "robot"
SPIDERS = "spider"
# SWING_COPTERS = "swing_copter"
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
# SWING_COPTERS_PREFIX = prefix(SWING_COPTERS)
EXPLOSIONS_PREFIX = prefix(EXPLOSIONS)
STREAKS_PREFIX = prefix(STREAKS)
COLORS_1_PREFIX = prefix(COLORS_1)
COLORS_2_PREFIX = prefix(COLORS_2)


V = TypeVar("V", bound="Values")


@define()
class Values(Binary):
    variables: Variables = field(factory=Variables)

    cubes: OrderedSet[int] = field(factory=ordered_set)
    ships: OrderedSet[int] = field(factory=ordered_set)
    balls: OrderedSet[int] = field(factory=ordered_set)
    ufos: OrderedSet[int] = field(factory=ordered_set)
    waves: OrderedSet[int] = field(factory=ordered_set)
    robots: OrderedSet[int] = field(factory=ordered_set)
    spiders: OrderedSet[int] = field(factory=ordered_set)
    # swing_copters: OrderedSet[int] = field(factory=ordered_set)
    explosions: OrderedSet[int] = field(factory=ordered_set)
    streaks: OrderedSet[int] = field(factory=ordered_set)
    colors_1: OrderedSet[int] = field(factory=ordered_set)
    colors_2: OrderedSet[int] = field(factory=ordered_set)

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary, order)

        self.variables.to_binary(binary, order, version)

        cubes = self.cubes

        writer.write_u16(len(cubes))

        iter(cubes).for_each(writer.write_u16)

        ships = self.ships

        writer.write_u8(len(ships))

        iter(ships).for_each(writer.write_u8)

        balls = self.balls

        writer.write_u8(len(balls))

        iter(balls).for_each(writer.write_u8)

        ufos = self.ufos

        writer.write_u8(len(ufos))

        iter(ufos).for_each(writer.write_u8)

        waves = self.waves

        writer.write_u8(len(waves))

        iter(waves).for_each(writer.write_u8)

        robots = self.robots

        writer.write_u8(len(robots))

        iter(robots).for_each(writer.write_u8)

        spiders = self.spiders

        writer.write_u8(len(spiders))

        iter(spiders).for_each(writer.write_u8)

        # swing_copters = self.swing_copters

        # writer.write_u8(len(swing_copters))

        # iter(swing_copters).for_each(writer.write_u8)

        explosions = self.explosions

        writer.write_u8(len(explosions))

        iter(explosions).for_each(writer.write_u8)

        streaks = self.streaks

        writer.write_u8(len(streaks))

        iter(streaks).for_each(writer.write_u8)

        colors_1 = self.colors_1

        writer.write_u8(len(colors_1))

        iter(colors_1).for_each(writer.write_u8)

        colors_2 = self.colors_2

        writer.write_u8(len(colors_2))

        iter(colors_2).for_each(writer.write_u8)

    @classmethod
    def from_binary(
        cls: Type[V],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> V:
        reader = Reader(binary, order)

        variables = Variables.from_binary(binary, order, version)

        cubes_length = reader.read_u16()

        cubes = iter.repeat_exactly_with(reader.read_u16, cubes_length).ordered_set()

        ships_length = reader.read_u8()

        ships = iter.repeat_exactly_with(reader.read_u8, ships_length).ordered_set()

        balls_length = reader.read_u8()

        balls = iter.repeat_exactly_with(reader.read_u8, balls_length).ordered_set()

        ufos_length = reader.read_u8()

        ufos = iter.repeat_exactly_with(reader.read_u8, ufos_length).ordered_set()

        waves_length = reader.read_u8()

        waves = iter.repeat_exactly_with(reader.read_u8, waves_length).ordered_set()

        robots_length = reader.read_u8()

        robots = iter.repeat_exactly_with(reader.read_u8, robots_length).ordered_set()

        spiders_length = reader.read_u8()

        spiders = iter.repeat_exactly_with(reader.read_u8, spiders_length).ordered_set()

        # swing_copters_length = reader.read_u8()

        # swing_copters = (
        #     iter.repeat_exactly_with(reader.read_u8, swing_copters_length).ordered_set()
        # )

        explosions_length = reader.read_u8()

        explosions = iter.repeat_exactly_with(reader.read_u8, explosions_length).ordered_set()

        streaks_length = reader.read_u8()

        streaks = iter.repeat_exactly_with(reader.read_u8, streaks_length).ordered_set()

        colors_1_length = reader.read_u8()

        colors_1 = iter.repeat_exactly_with(reader.read_u8, colors_1_length).ordered_set()

        colors_2_length = reader.read_u8()

        colors_2 = iter.repeat_exactly_with(reader.read_u8, colors_2_length).ordered_set()

        return cls(
            variables=variables,
            cubes=cubes,
            ships=ships,
            balls=balls,
            ufos=ufos,
            waves=waves,
            robots=robots,
            spiders=spiders,
            # swing_copters=swing_copters,
            explosions=explosions,
            streaks=streaks,
            colors_1=colors_1,
            colors_2=colors_2,
        )

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
            # SWING_COPTERS_PREFIX: self.swing_copters,
            EXPLOSIONS_PREFIX: self.explosions,
            STREAKS_PREFIX: self.streaks,
            COLORS_1_PREFIX: self.colors_1,
            COLORS_2_PREFIX: self.colors_2,
        }

    @classmethod
    def from_robtop_data(cls: Type[V], data: StringMapping[str]) -> V:  # type: ignore
        self = cls(variables=Variables.from_robtop_data(data))

        for prefix, ordered_set in self.prefix_to_ordered_set.items():
            length = len(prefix)

            for name in data.keys():
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
