from __future__ import annotations

from datetime import timedelta
# from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterable, Optional, Type, TypeVar

from attrs import define, field
from iters import iter

# from gd.api.editor import Editor
from gd.await_iters import wrap_await_iter
from gd.constants import COMMENT_PAGE_SIZE, DEFAULT_PAGE, DEFAULT_RECORD, EMPTY
# from gd.decorators import cache_by
from gd.entity import Entity
from gd.enums import (
    CommentStrategy,
    DemonDifficulty,
    Difficulty,
    LevelDifficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    Score,
    TimelyID,
    TimelyType,
)
from gd.errors import MissingAccess
# from gd.models import LevelModel
from gd.password import Password
from gd.song import Song
from gd.user import User
from gd.versions import CURRENT_GAME_VERSION, GameVersion

if TYPE_CHECKING:
    from gd.client import Client  # noqa
    from gd.comments import Comment  # noqa

__all__ = ("Level",)

L = TypeVar("L", bound="Level")


@define()
class Level(Entity):
    name: str = field()
    creator: User = field()
    song: Song = field()
    description: str = field(default=EMPTY)
    # data
    version: int = field(default=0)
    downloads: int = field(default=0)
    game_version: GameVersion = field(default=CURRENT_GAME_VERSION)
    rating: int = field(default=0)
    length: LevelLength = field(default=LevelLength.DEFAULT)
    difficulty: Difficulty = field(default=Difficulty.DEFAULT)
    stars: int = field(default=0)
    requested_stars: int = field(default=0)
    score: int = field(default=0)
    password_data: Password = field(factory=Password)
    # uploaded_at: datetime
    # updated_at: datetime
    original_id: int = field(default=0)
    two_player: bool = field(default=False)
    # extra_data
    coins: int = field(default=0)
    verified_coins: bool = field(default=False)
    low_detail_mode: bool = field(default=False)
    epic: bool = field(default=False)
    object_count: int = field(default=0)
    editor_time: timedelta = field(factory=timedelta)
    copies_time: timedelta = field(factory=timedelta)
    timely_type: TimelyType = field(default=TimelyType.DEFAULT)
    timely_id: TimelyID = field(default=TimelyID.DEFAULT)

    @classmethod
    def official(
        cls: Type[L],
        id: Optional[int] = None,
        name: Optional[str] = None,
        get_data: bool = True,
        server_style: bool = False,
    ) -> L:
        official_levels = OFFICIAL_LEVELS

        if id is None:
            if name is None:
                ...

            else:
                official_level = iter(official_levels).find_or_none(by_name(name))

        else:
            official_level = iter(official_levels).find_or_none(by_id(id))


        if official_level is None:
            raise LookupError("Could not find official level by given query.")

        return cast(OfficialLevel, official_level).into_level(
            client, get_data=get_data, server_style=server_style
        )

    @property
    def score_type(self) -> Score:
        return Score(self.score)

    @property
    def password(self) -> Optional[int]:
        return self.password_data.password

    def is_copyable(self) -> bool:
        return self.password_data.copyable

    def is_timely(self, timely_type: Optional[TimelyType] = None) -> bool:
        if timely_type is None:
            return self.timely_type is not TimelyType.NOT_TIMELY

        return self.timely_type is timely_type

    def is_rated(self) -> bool:
        return self.stars > 0

    def is_unfeatured(self) -> bool:
        return self.score_type.is_unfeatured()

    def is_epic_only(self) -> bool:
        return self.score_type.is_epic_only()

    def is_featured(self) -> bool:
        return self.score_type.is_featured()

    def is_epic(self) -> bool:
        return self.epic

    def is_original(self) -> bool:
        return not self.original_id

    def open_editor(self) -> Editor:
        ...

    async def report(self) -> None:
        await self.client.report_level(self)

    async def upload(self, **kwargs: Any) -> None:
        song = self.song
        song_id = song.id

        track_id, song_id = (0, song_id) if song.is_custom() else (song_id, 0)

        args = dict(
            name=self.name,
            id=self.id,
            version=self.version,
            length=abs(self.length.value),
            track_id=track_id,
            song_id=song_id,
            two_player=self.has_two_player(),
            is_auto=self.is_auto(),
            original=self.original_id,
            objects=self.objects,
            coins=self.coins,
            stars=self.stars,
            unlisted=False,
            friends_only=False,
            low_detail_mode=self.has_low_detail_mode(),
            password=self.password,
            copyable=self.is_copyable(),
            description=self.description,
            editor_seconds=self.editor_seconds,
            copies_seconds=self.copies_seconds,
            data=self.data,
        )

        args.update(kwargs)

        uploaded = await client.upload_level(**args)

        self.options.update(uploaded.options)

    async def delete(self) -> None:
        await self.client.delete_level(self)

    async def update_description(self, content: str) -> None:
        await self.client.update_level_description(self, content)

    async def rate(self, stars: int) -> None:
        await self.client.rate_level(self, stars)

    async def rate_demon(
        self, demon_difficulty: DemonDifficulty = DemonDifficulty.DEFAULT, as_mod: bool = False
    ) -> None:
        await self.client.rate_demon(self, demon_difficulty=demon_difficulty, as_mod=as_mod)

    async def send(self, stars: int, featured: bool) -> None:
        await self.client.send_level(self, stars=stars, featured=featured)

    async def is_alive(self) -> bool:
        ...

    async def update(self, *, get_data: bool = True) -> Optional[Level]:
        ...

    async def comment(self, content: str, record: int = DEFAULT_RECORD) -> Optional[Comment]:
        return await self.client.comment_level(self, content, record)

    async def like(self) -> None:
        await self.client.like(self)

    async def dislike(self) -> None:
        await self.client.dislike(self)

    @wrap_await_iter
    def get_leaderboard(
        self,
        strategy: LevelLeaderboardStrategy = LevelLeaderboardStrategy.DEFAULT,
    ) -> AsyncIterator[User]:
        return self.client.get_level_leaderboard(self, strategy=strategy)

    @wrap_await_iter
    def get_comments(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        pages: Iterable[int] = DEFAULT_PAGE,
        amount: int = COMMENT_PAGE_SIZE,
    ) -> AsyncIterator["Comment"]:
        return self.client.get_level_comments(
            level=self,
            strategy=strategy,
            pages=pages,
            amount=amount,
            concurrent=concurrent,
        )

    @wrap_await_iter
    def get_comments_on_page(
        self,
        strategy: CommentStrategy = CommentStrategy.DEFAULT,
        page: int = DEFAULT_PAGE,
        count: int = COMMENT_PAGE_SIZE,
    ) -> AsyncIterator[Comment]:
        return self.client.get_level_comments_on_page(
            self, page=page, count=count, strategy=strategy
        )
