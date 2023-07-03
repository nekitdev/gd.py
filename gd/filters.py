from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set
from typing_extensions import TypedDict

from gd.binary import VERSION, Binary, BinaryReader, BinaryWriter
from gd.binary_utils import Reader, Writer
from gd.enums import ByteOrder, Difficulty, LevelLength, RateFilter, SearchStrategy, SpecialRateType
from gd.string_constants import DASH
from gd.string_utils import concat_comma, wrap

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

COMPLETED_BIT = 0b00000001
COMPLETED_SET_BIT = 0b00000010
REQUIRE_COINS_BIT = 0b00000100
RATE_FILTER_SET_BIT = 0b00001000
REQUIRE_TWO_PLAYER_BIT = 0b00010000
CUSTOM_SONG_BIT = 0b00100000
SONG_ID_SET_BIT = 0b01000000
REQUIRE_ORIGINAL_BIT = 0b10000000


def level_difficulty_value(difficulty: Difficulty) -> int:
    return difficulty.into_level_difficulty().value


def difficulty_value(difficulty: Difficulty) -> int:
    return difficulty.value


def length_value(length: LevelLength) -> int:
    return length.value


@define()
class Filters(Binary):
    strategy: SearchStrategy = field(default=SearchStrategy.DEFAULT)
    difficulties: OrderedSet[Difficulty] = field(
        factory=ordered_set, converter=ordered_set  # type: ignore
    )
    lengths: OrderedSet[LevelLength] = field(
        factory=ordered_set, converter=ordered_set  # type: ignore
    )
    completed_levels: OrderedSet[int] = field(
        factory=ordered_set, converter=ordered_set  # type: ignore
    )
    completed: Optional[bool] = field(default=DEFAULT_COMPLETED)
    require_coins: bool = field(default=DEFAULT_REQUIRE_COINS)
    rate_filter: Optional[RateFilter] = field(default=DEFAULT_RATE_FILTER)
    require_two_player: bool = field(default=DEFAULT_REQUIRE_TWO_PLAYER)
    song_id: Optional[int] = field(default=DEFAULT_SONG_ID)
    custom_song: bool = field(default=DEFAULT_CUSTOM_SONG)
    require_original: bool = field(default=DEFAULT_REQUIRE_ORIGINAL)
    followed: OrderedSet[int] = field(factory=ordered_set, converter=ordered_set)  # type: ignore

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

        reader = Reader(binary, order)

        strategy_value = reader.read_u8()

        strategy = SearchStrategy(strategy_value)

        difficulties_length = reader.read_u8()

        difficulties = (
            iter.repeat_exactly_with(reader.read_u8, difficulties_length)
            .map(Difficulty)
            .ordered_set()
        )

        lengths_length = reader.read_u8()

        lengths = (
            iter.repeat_exactly_with(reader.read_u8, lengths_length).map(LevelLength).ordered_set()
        )

        completed_levels_length = reader.read_u32()

        completed_levels = iter.repeat_exactly_with(
            reader.read_u32, completed_levels_length
        ).ordered_set()

        value = reader.read_u8()

        completed: Optional[bool]

        completed = value & completed_bit == completed_bit

        completed_set = value & completed_set_bit == completed_set_bit

        if not completed_set:
            completed = None

        require_coins = value & require_coins_bit == require_coins_bit

        rate_filter_set = value & rate_filter_set_bit == rate_filter_set_bit

        if rate_filter_set:
            rate_filter_value = reader.read_u8()

            rate_filter = RateFilter(rate_filter_value)

        else:
            rate_filter = None

        require_two_player = value & require_two_player_bit == require_two_player_bit

        custom_song = value & custom_song_bit == custom_song_bit

        song_id_set = value & song_id_set_bit == song_id_set_bit

        if song_id_set:
            song_id = reader.read_u32()

        else:
            song_id = None

        require_original = value & require_original_bit == require_original_bit

        followed_length = reader.read_u32()

        followed = iter.repeat_exactly_with(reader.read_u32, followed_length).ordered_set()

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
        writer = Writer(binary, order)

        writer.write_u8(self.strategy.value)

        difficulties = self.difficulties

        writer.write_u8(len(difficulties))

        iter(difficulties).map(difficulty_value).for_each(writer.write_u8)

        lengths = self.lengths

        writer.write_u8(len(lengths))

        iter(lengths).map(length_value).for_each(writer.write_u8)

        completed_levels = self.completed_levels

        writer.write_u32(len(completed_levels))

        iter(completed_levels).for_each(writer.write_u32)

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

        if self.require_two_player:
            value |= REQUIRE_TWO_PLAYER_BIT

        if self.custom_song:
            value |= CUSTOM_SONG_BIT

        song_id = self.song_id

        if song_id is not None:
            value |= SONG_ID_SET_BIT

        if self.require_original:
            value |= REQUIRE_ORIGINAL_BIT

        writer.write_u8(value)

        if rate_filter is not None:
            writer.write_u8(rate_filter.value)

        if song_id is not None:
            writer.write_u32(song_id)

        followed = self.followed

        writer.write_u32(len(followed))

        iter(followed).for_each(writer.write_u32)

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
        custom: bool,
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
            custom_song=custom,
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
            not_rated = rate_filter.is_not_rated()

            if not_rated:
                filters.update(RobTopFilters(no_star=int(not_rated)))

            rated = rate_filter.is_rated()

            if rated:
                filters.update(RobTopFilters(star=int(rated)))

            featured = rate_filter.is_featured()

            if featured:
                filters.update(RobTopFilters(featured=int(featured)))

            special_rate_type = SpecialRateType.NONE

            if rate_filter.is_epic():
                special_rate_type = SpecialRateType.EPIC

            if rate_filter.is_godlike():
                special_rate_type = SpecialRateType.GODLIKE

            if not special_rate_type.is_none():
                filters.update(RobTopFilters(epic=special_rate_type.value))

        filters.update(
            RobTopFilters(
                type=self.strategy.value,
                diff=iter(self.difficulties)
                .map(level_difficulty_value)
                .map(str)
                .collect(concat_comma)
                or DASH,
                len=iter(self.lengths).map(length_value).map(str).collect(concat_comma) or DASH,
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
                RobTopFilters(
                    completed_levels=wrap(iter(completed_levels).map(str).collect(concat_comma))
                )
            )

        followed = self.followed

        if followed:
            filters.update(RobTopFilters(followed=iter(followed).map(str).collect(concat_comma)))

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
