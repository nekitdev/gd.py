from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Optional, Type, TypeVar

from attrs import define, field
from typing_extensions import TypedDict

from gd.enums import Difficulty, LevelLength, SearchStrategy
from gd.string_constants import DASH
from gd.string_utils import concat_comma, wrap
from gd.typing import DynamicTuple

__all__ = ("Filters",)

if TYPE_CHECKING:
    from gd.client import Client


F = TypeVar("F", bound="Filters")


@define()
class Filters:
    strategy: SearchStrategy = field(default=SearchStrategy.DEFAULT)
    difficulties: DynamicTuple[Difficulty] = field(default=(), converter=tuple)
    lengths: DynamicTuple[LevelLength] = field(default=(), converter=tuple)
    completed_levels: DynamicTuple[int] = field(default=(), converter=tuple)
    completed: Optional[bool] = field(default=None)
    require_coins: bool = field(default=False)
    featured: bool = field(default=False)
    epic: bool = field(default=False)
    rated: Optional[bool] = field(default=None)
    require_two_player: bool = field(default=False)
    song_id: Optional[int] = field(default=None)
    custom_song: bool = field(default=False)
    require_original: bool = field(default=False)
    followed: DynamicTuple[int] = field(default=(), converter=tuple)

    @classmethod
    def by_user(cls: Type[F], *args: Any, **kwargs: Any) -> F:  # type: ignore
        return cls(SearchStrategy.BY_USER, *args, **kwargs)  # type: ignore

    @classmethod
    def with_song(  # type: ignore
        cls: Type[F], *args: Any, song_id: int, custom_song: bool, **kwargs: Any
    ) -> F:
        return cls(*args, song_id=song_id, custom_song=custom_song, **kwargs)  # type: ignore

    @classmethod
    def search_many(cls: Type[F], *args: Any, **kwargs: Any) -> F:  # type: ignore
        return cls(SearchStrategy.SEARCH_MANY, *args, **kwargs)  # type: ignore

    @classmethod
    def with_followed(  # type: ignore
        cls: Type[F], *args: Any, followed: Iterable[int], **kwargs: Any
    ) -> F:
        return cls(SearchStrategy.FOLLOWED, *args, followed=followed, **kwargs)  # type: ignore

    @classmethod
    def with_completed_levels(  # type: ignore
        cls: Type[F], *args: Any, completed_levels: Iterable[int], **kwargs: Any
    ) -> F:
        return cls(*args, completed_levels=completed_levels, **kwargs)  # type: ignore

    @classmethod
    def by_friends(cls: Type[F], *args: Any, **kwargs: Any) -> F:  # type: ignore
        return cls(SearchStrategy.FRIENDS, *args, **kwargs)  # type: ignore

    @classmethod
    def client_followed(  # type: ignore
        cls: Type[F], client: Client, *args: Any, **kwargs: Any
    ) -> F:
        return cls.with_followed(*args, followed=client.database.followed, **kwargs)  # type: ignore

    # @classmethod
    # def client_completed_levels(  # type: ignore
    #     cls: Type[F], client: Client, *args: Any, **kwargs: Any
    # ) -> F:
    #     return cls.with_completed(  # type: ignore
    #         *args, completed_levels=..., **kwargs
    #     )

    def to_robtop_filters(self) -> RobTopFilters:
        filters = RobTopFilters(
            type=self.strategy.value,
            diff=concat_comma(
                map(
                    str,
                    (difficulty.into_level_difficulty().value for difficulty in self.difficulties),
                )
            )
            or DASH,
            len=concat_comma(map(str, (length.value for length in self.lengths))) or DASH,
            featured=int(self.featured),
            original=int(self.require_original),
            two_player=int(self.require_two_player),
            coins=int(self.require_coins),
            epic=int(self.epic),
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

        rated = self.rated

        if rated is not None:
            if rated:
                filters.update(RobTopFilters(star=int(rated)))

            else:
                filters.update(RobTopFilters(no_star=int(not rated)))

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
