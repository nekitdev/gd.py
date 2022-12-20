from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from typing_extensions import TypedDict

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder, Difficulty, LevelLength, RateFilter, SearchStrategy
from gd.string_constants import DASH
from gd.string_utils import concat_comma, wrap
from gd.typing import DynamicTuple

__all__ = ("Filters",)

if TYPE_CHECKING:
    from gd.client import Client


F = TypeVar("F", bound="Filters")

DEFAULT_ITERABLE = ()
DEFAULT_COMPLETED = None
DEFAULT_REQUIRE_COINS = False
DEFAULT_RATE_FILTER = None
DEFAULT_REQUIRE_TWO_PLAYER = False
DEFAULT_SONG_ID = None
DEFAULT_CUSTOM_SONG = False
DEFAULT_REQUIRE_ORIGINAL = False

GODLIKE = 2

COMPLETED_BIT = 0b00000001
COMPLETED_SET_BIT = 0b00000010
REQUIRE_COINS_BIT = 0b00000100
RATE_FILTER_SET_BIT = 0b00001000
REQUIRE_TWO_PLAYER_BIT = 0b00010000
CUSTOM_SONG_BIT = 0b00100000
SONG_ID_SET_BIT = 0b01000000
REQUIRE_ORIGINAL_BIT = 0b10000000


@define()
class Filters(Binary):
    strategy: SearchStrategy = field(default=SearchStrategy.DEFAULT)
    difficulties: OrderedSet[Difficulty] = field(factory=ordered_set, converter=ordered_set)
    lengths: OrderedSet[LevelLength] = field(factory=ordered_set, converter=ordered_set)
    completed_levels: OrderedSet[int] = field(factory=ordered_set, converter=ordered_set)
    completed: Optional[bool] = field(default=DEFAULT_COMPLETED)
    require_coins: bool = field(default=DEFAULT_REQUIRE_COINS)
    rate_filter: Optional[RateFilter] = field(default=DEFAULT_RATE_FILTER)
    require_two_player: bool = field(default=DEFAULT_REQUIRE_TWO_PLAYER)
    song_id: Optional[int] = field(default=DEFAULT_SONG_ID)
    custom_song: bool = field(default=DEFAULT_CUSTOM_SONG)
    require_original: bool = field(default=DEFAULT_REQUIRE_ORIGINAL)
    followed: OrderedSet[int] = field(factory=ordered_set, converter=ordered_set)

    @classmethod
    def from_binary(
        cls: Type[F],
        binary: BinaryReader,
        order: ByteOrder = ByteOrder.DEFAULT,
        version: int = VERSION,
    ) -> F:
        completed_bit = COMPLETED_BIT
        completed_set_bit = COMPLETED_SET_BIT
        require_coins_bit = REQUIRE_COINS_BIT
        rate_filter_set_bit = RATE_FILTER_SET_BIT
        require_two_player_bit = REQUIRE_TWO_PLAYER_BIT
        custom_song_bit = CUSTOM_SONG_BIT
        song_id_set_bit = SONG_ID_SET_BIT
        require_original_bit = REQUIRE_ORIGINAL_BIT

        reader = Reader(binary)

        strategy_value = reader.read_u8(order)

        strategy = SearchStrategy(strategy_value)

        read_u8 = partial(reader.read_u8, order)

        difficulties_length = reader.read_u8(order)

        difficulties = iter.repeat_exactly_with(read_u8, difficulties_length).map(
            Difficulty
        ).ordered_set()

        lengths_length = reader.read_u8(order)

        lengths = iter.repeat_exactly_with(read_u8, lengths_length).map(LevelLength).ordered_set()

        read_u32 = partial(reader.read_u32, order)

        completed_levels_length = reader.read_u32(order)

        completed_levels = iter.repeat_exactly_with(read_u32, completed_levels_length).ordered_set()

        value = reader.read_u8(order)

        completed = value & completed_bit == completed_bit

        completed_set = value & completed_set_bit == completed_set_bit

        if not completed_set:
            completed = None

        require_coins = value & require_coins_bit == require_coins_bit

        rate_filter_set = value & rate_filter_set_bit == rate_filter_set_bit

        if rate_filter_set:
            rate_filter_value = reader.read_u8(order)

            rate_filter = RateFilter(rate_filter_value)

        else:
            rate_filter = None

        require_two_player = value & require_two_player_bit == require_two_player_bit

        custom_song = value & custom_song_bit == custom_song_bit

        song_id_set = value & song_id_set_bit == song_id_set_bit

        if song_id_set:
            song_id = reader.read_u32(order)

        else:
            song_id = None

        require_original = value & require_original_bit == require_original_bit

        followed_length = reader.read_u16(order)

        followed = iter.repeat_exactly_with(read_u32, followed_length).ordered_set()

        return cls(
            strategy=strategy,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    def to_binary(
        self, binary: BinaryWriter, order: ByteOrder = ByteOrder.DEFAULT, version: int = VERSION
    ) -> None:
        writer = Writer(binary)

        writer.write_u8(self.strategy.value, order)

        difficulties = self.difficulties

        writer.write_u8(len(difficulties), order)

        for difficulty in difficulties:
            writer.write_u8(difficulty.value, order)

        lengths = self.lengths

        writer.write_u8(len(lengths), order)

        for length in lengths:
            writer.write_u8(length.value, order)

        completed_levels = self.completed_levels

        writer.write_u32(len(completed_levels), order)

        for level_id in completed_levels:
            writer.write_u32(level_id, order)

        value = 0

        completed = self.completed

        if completed is not None:
            if completed:
                value |= COMPLETED_BIT

            value |= COMPLETED_SET_BIT

        if self.require_coins:
            value |= REQUIRE_COINS_BIT

        rate_filter = self.rate_filter

        if rate_filter is not None:
            value |= RATE_FILTER_SET_BIT

            writer.write_u8(rate_filter.value, order)

        if self.require_two_player:
            value |= REQUIRE_TWO_PLAYER_BIT

        if self.custom_song:
            value |= CUSTOM_SONG_BIT

        song_id = self.song_id

        if song_id is not None:
            value |= SONG_ID_SET_BIT

            writer.write_u32(song_id, order)

        if self.require_original:
            value |= REQUIRE_ORIGINAL_BIT

        writer.write_u8(value, order)

        followed = self.followed

        writer.write_u32(len(followed), order)

        for account_id in followed:
            writer.write_u32(account_id, order)

    @classmethod
    def create(
        cls: Type[F],
        strategy: SearchStrategy = SearchStrategy.DEFAULT,
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls(
            strategy=strategy,
            difficulties=difficulties,  # type: ignore
            lengths=lengths,  # type: ignore
            completed_levels=completed_levels,  # type: ignore
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore
        )

    @classmethod
    def by_user(
        cls: Type[F],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls.create(
            strategy=SearchStrategy.BY_USER,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    @classmethod
    def with_song(
        cls: Type[F],
        song_id: int,
        custom_song: bool,
        strategy: SearchStrategy = SearchStrategy.DEFAULT,
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls.create(
            strategy=strategy,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    @classmethod
    def search_many(
        cls: Type[F],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls.create(
            strategy=SearchStrategy.SEARCH_MANY,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    @classmethod
    def with_followed(
        cls: Type[F],
        followed: Iterable[int],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
    ) -> F:
        return cls.create(
            strategy=SearchStrategy.FOLLOWED,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    @classmethod
    def with_completed_levels(
        cls: Type[F],
        completed_levels: Iterable[int],
        strategy: SearchStrategy = SearchStrategy.DEFAULT,
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls.create(
            strategy=strategy,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    @classmethod
    def by_friends(
        cls: Type[F],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls.create(
            strategy=SearchStrategy.FRIENDS,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,
        )

    @classmethod
    def client_followed(
        cls: Type[F],
        client: Client,
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
    ) -> F:
        return cls.with_followed(
            client.database.followed,
            difficulties=difficulties,
            lengths=lengths,
            completed_levels=completed_levels,
            completed=completed,
            require_coins=require_coins,
            rate_filter=rate_filter,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
        )

    # @classmethod
    # def client_completed_levels(
    #     cls: Type[F],
    #     client: Client,
    #     strategy: SearchStrategy = SearchStrategy.DEFAULT,
    #     difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
    #     lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
    #     completed: Optional[bool] = DEFAULT_COMPLETED,
    #     require_coins: bool = DEFAULT_REQUIRE_COINS,
    #     rate_filter: Optional[RateFilter] = DEFAULT_RATE_FILTER,
    #     require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
    #     song_id: Optional[int] = DEFAULT_SONG_ID,
    #     custom_song: bool = DEFAULT_CUSTOM_SONG,
    #     require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
    #     followed: Iterable[int] = DEFAULT_ITERABLE,
    # ) -> F:
    #     return cls.with_completed_levels(
    #         ...,
    #         strategy=strategy,
    #         difficulties=difficulties,
    #         lengths=lengths,
    #         completed=completed,
    #         require_coins=require_coins,
    #         rate_filter=rate_filter,
    #         require_two_player=require_two_player,
    #         song_id=song_id,
    #         custom_song=custom_song,
    #         require_original=require_original,
    #         followed=followed,
    #     )

    def to_robtop_filters(self) -> RobTopFilters:
        filters = RobTopFilters()

        rate_filter = self.rate_filter

        if rate_filter is not None:
            if rate_filter.is_not_rated():
                filters.update(RobTopFilters(no_star=int(True)))

            if rate_filter.is_rated():
                filters.update(RobTopFilters(star=int(True)))

            if rate_filter.is_featured():
                filters.update(RobTopFilters(featured=int(True)))

            if rate_filter.is_epic():
                filters.update(RobTopFilters(epic=int(True)))

            if rate_filter.is_godlike():
                filters.update(RobTopFilters(epic=GODLIKE))  # why

        filters.update(
            RobTopFilters(
                type=self.strategy.value,
                diff=concat_comma(
                    map(
                        str,
                        (
                            difficulty.into_level_difficulty().value
                            for difficulty in self.difficulties
                        ),
                    )
                )
                or DASH,
                len=concat_comma(map(str, (length.value for length in self.lengths))) or DASH,
                original=int(self.require_original),
                two_player=int(self.require_two_player),
                coins=int(self.require_coins),
            )
        )

        completed = self.completed

        if completed is not None:
            if completed:
                filters.update(RobTopFilters(only_completed=int(completed)))

            else:
                filters.update(RobTopFilters(uncompleted=int(not completed)))

        completed_levels = self.completed_levels

        if completed_levels:
            filters.update(
                RobTopFilters(completed_levels=wrap(concat_comma(map(str, completed_levels))))
            )

        followed = self.followed

        if followed:
            filters.update(RobTopFilters(followed=concat_comma(map(str, followed))))

        song_id = self.song_id

        if song_id is not None:
            filters.update(RobTopFilters(song=song_id, custom_song=int(self.custom_song)))

        return filters


class RobTopFilters(TypedDict, total=False):
    type: int
    diff: str
    len: str
    uncompleted: int
    only_completed: int
    featured: int
    original: int
    two_player: int
    coins: int
    epic: int
    completed_levels: str
    star: int
    no_star: int
    followed: str
    song: int
    custom_song: int
