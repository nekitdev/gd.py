from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional, Type, TypeVar

from attrs import define, field
from typing_extensions import TypedDict

from gd.enums import Difficulty, LevelLength, RateType, SearchStrategy
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
DEFAULT_RATE_TYPE = None
DEFAULT_REQUIRE_TWO_PLAYER = False
DEFAULT_SONG_ID = None
DEFAULT_CUSTOM_SONG = False
DEFAULT_REQUIRE_ORIGINAL = False


@define()
class Filters:
    strategy: SearchStrategy = field(default=SearchStrategy.DEFAULT)
    difficulties: DynamicTuple[Difficulty] = field(default=DEFAULT_ITERABLE, converter=tuple)
    lengths: DynamicTuple[LevelLength] = field(default=DEFAULT_ITERABLE, converter=tuple)
    completed_levels: DynamicTuple[int] = field(default=DEFAULT_ITERABLE, converter=tuple)
    completed: Optional[bool] = field(default=DEFAULT_COMPLETED)
    require_coins: bool = field(default=DEFAULT_REQUIRE_COINS)
    rate_type: Optional[RateType] = field(default=DEFAULT_RATE_TYPE)
    require_two_player: bool = field(default=DEFAULT_REQUIRE_TWO_PLAYER)
    song_id: Optional[int] = field(default=DEFAULT_SONG_ID)
    custom_song: bool = field(default=DEFAULT_CUSTOM_SONG)
    require_original: bool = field(default=DEFAULT_REQUIRE_ORIGINAL)
    followed: DynamicTuple[int] = field(default=DEFAULT_ITERABLE, converter=tuple)

    @classmethod
    def by_user(
        cls: Type[F],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls(
            strategy=SearchStrategy.BY_USER,
            difficulties=difficulties,  # type: ignore  # XXX: well...
            lengths=lengths,  # type: ignore  # XXX: well...
            completed_levels=completed_levels,  # type: ignore  # XXX: well...
            completed=completed,
            require_coins=require_coins,
            rate_type=rate_type,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore  # XXX: well...
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
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls(
            strategy=strategy,
            difficulties=difficulties,  # type: ignore  # XXX: well...
            lengths=lengths,  # type: ignore  # XXX: well...
            completed_levels=completed_levels,  # type: ignore  # XXX: well...
            completed=completed,
            require_coins=require_coins,
            rate_type=rate_type,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore  # XXX: well...
        )

    @classmethod
    def search_many(
        cls: Type[F],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls(
            strategy=SearchStrategy.SEARCH_MANY,
            difficulties=difficulties,  # type: ignore  # XXX: well..
            lengths=lengths,  # type: ignore  # XXX: well..
            completed_levels=completed_levels,  # type: ignore  # XXX: well..
            completed=completed,
            require_coins=require_coins,
            rate_type=rate_type,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore  # XXX: well..
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
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
    ) -> F:
        return cls(
            strategy=SearchStrategy.FOLLOWED,
            difficulties=difficulties,  # type: ignore  # XXX: well...
            lengths=lengths,  # type: ignore  # XXX: well...
            completed_levels=completed_levels,  # type: ignore  # XXX: well...
            completed=completed,
            require_coins=require_coins,
            rate_type=rate_type,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore  # XXX: well...
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
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
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
            rate_type=rate_type,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore
        )

    @classmethod
    def by_friends(
        cls: Type[F],
        difficulties: Iterable[Difficulty] = DEFAULT_ITERABLE,
        lengths: Iterable[LevelLength] = DEFAULT_ITERABLE,
        completed_levels: Iterable[int] = DEFAULT_ITERABLE,
        completed: Optional[bool] = DEFAULT_COMPLETED,
        require_coins: bool = DEFAULT_REQUIRE_COINS,
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
        require_two_player: bool = DEFAULT_REQUIRE_TWO_PLAYER,
        song_id: Optional[int] = DEFAULT_SONG_ID,
        custom_song: bool = DEFAULT_CUSTOM_SONG,
        require_original: bool = DEFAULT_REQUIRE_ORIGINAL,
        followed: Iterable[int] = DEFAULT_ITERABLE,
    ) -> F:
        return cls(
            strategy=SearchStrategy.FRIENDS,
            difficulties=difficulties,  # type: ignore
            lengths=lengths,  # type: ignore
            completed_levels=completed_levels,  # type: ignore
            completed=completed,
            require_coins=require_coins,
            rate_type=rate_type,
            require_two_player=require_two_player,
            song_id=song_id,
            custom_song=custom_song,
            require_original=require_original,
            followed=followed,  # type: ignore
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
        rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
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
            rate_type=rate_type,
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
    #     rate_type: Optional[RateType] = DEFAULT_RATE_TYPE,
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
    #         rate_type=rate_type,
    #         require_two_player=require_two_player,
    #         song_id=song_id,
    #         custom_song=custom_song,
    #         require_original=require_original,
    #         followed=followed,
    #     )

    def to_robtop_filters(self) -> RobTopFilters:
        filters = RobTopFilters()

        rate_type = self.rate_type

        if rate_type is not None:
            if rate_type.is_not_rated():
                filters.update(RobTopFilters(no_star=1))

            if rate_type.is_rated():
                filters.update(RobTopFilters(star=1))

            if rate_type.is_featured():
                filters.update(RobTopFilters(featured=1))

            if rate_type.is_epic():
                filters.update(RobTopFilters(epic=1))

            if rate_type.is_godlike():
                filters.update(RobTopFilters(epic=2))

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
