from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters.iters import iter
from iters.ordered_set import OrderedSet, ordered_set

from gd.enums import Difficulty, LevelLength, RateFilter, SearchStrategy, SpecialRateType
from gd.string_constants import DASH
from gd.string_utils import concat_comma, wrap
from gd.typing import Data

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


def level_difficulty_value(difficulty: Difficulty) -> int:
    return difficulty.into_level_difficulty().value


def difficulty_value(difficulty: Difficulty) -> int:
    return difficulty.value


def length_value(length: LevelLength) -> int:
    return length.value


@define()
class Filters:
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


class RobTopFilters(Data, total=False):
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
