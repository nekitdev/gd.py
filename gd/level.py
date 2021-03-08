import json
from pathlib import Path

from attr import attrib, dataclass
from iters import iter

from gd.abstract_entity import AbstractEntity
from gd.api.editor import Editor
from gd.async_iters import awaitable_iterator
from gd.converters import GameVersion
from gd.crypto import unzip_level_str, zip_level_str
from gd.datetime import datetime, timedelta
from gd.decorators import cache_by
from gd.enums import (
    CommentStrategy,
    DemonDifficulty,
    LevelDifficulty,
    LevelLeaderboardStrategy,
    LevelLength,
    TimelyType,
)
from gd.errors import MissingAccess
from gd.logging import get_logger
from gd.model import LevelModel  # type: ignore
from gd.song import Song
from gd.text_utils import is_level_probably_decoded, make_repr, object_count
from gd.typing import TYPE_CHECKING, Any, AsyncIterator, Dict, Iterable, Optional, Type, Union, cast
from gd.user import User

if TYPE_CHECKING:
    from gd.client import Client  # noqa
    from gd.comment import Comment  # noqa

__all__ = ("Level", "official_levels", "official_levels_data")

CONCURRENT = True
COMMENT_PAGE_SIZE = 20
ZERO_PAGE = (0,)


official_levels_path = Path(__file__).parent / "official_levels.json"
official_levels_data: Dict[str, str] = {}

log = get_logger(__name__)


class Level(AbstractEntity):
    """Class that represents a Geometry Dash Level.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)

            Return name of the level.

        .. describe:: repr(x)

            Return representation of the level, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __init__(self, *, client: Optional["Client"] = None, **options) -> None:
        options.setdefault("unprocessed_data", zip_level_str(options.get("data", "")))
        super().__init__(client=client, **options)

    def __repr__(self) -> str:
        info = {
            "id": self.id,
            "name": repr(self.name),
            "creator": self.creator,
            "version": self.version,
            "difficulty": self.difficulty,
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.name)

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()

        result.update(
            editor_time=self.editor_time,
            copies_time=self.copies_time,
            featured=self.is_featured(),
            was_unfeatured=self.was_unfeatured(),
        )

        return result

    @classmethod
    def from_model(  # type: ignore
        cls,
        model: LevelModel,
        *,
        client: Optional["Client"] = None,
        creator: Optional[User] = None,
        song: Optional[Song] = None,
        type: Optional[TimelyType] = None,
        timely_id: int = 0,
        cooldown: int = -1,
    ) -> "Level":
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            unprocessed_data=model.unprocessed_data,
            version=model.version,
            creator=(creator if creator else User()).attach_client(client),
            song=(song if song else Song()).attach_client(client),
            downloads=model.downloads,
            game_version=model.game_version,
            rating=model.rating,
            length=model.length,
            demon=model.demon,
            stars=model.stars,
            score=model.score,
            auto=model.auto,
            password=model.password,
            copyable=model.copyable,
            difficulty=model.difficulty,
            uploaded_at=model.uploaded_at,
            updated_at=model.updated_at,
            original_id=model.original_id,
            two_player=model.two_player,
            extra_string=model.extra_string,
            coins=model.coins,
            verified_coins=model.verified_coins,
            requested_stars=model.requested_stars,
            low_detail_mode=model.low_detail_mode,
            epic=model.epic,
            object_count=model.object_count,
            editor_seconds=model.editor_seconds,
            copies_seconds=model.copies_seconds,
            timely_id=(timely_id if timely_id > 0 else model.timely_id),
            type=(model.type if type is None else type),
            cooldown=cooldown,
            client=client,
        )

    @classmethod
    def official(
        cls,
        id: Optional[int] = None,
        name: Optional[str] = None,
        index: Optional[int] = None,
        client: Optional["Client"] = None,
        get_data: bool = True,
        server_style: bool = False,
    ) -> "Level":
        """Get official level to work with.

        Lookup is done in the following form: ``id -> name -> index``.

        Parameters
        ----------
        id: Optional[:class:`int`]
            ID of the official level.

        name: Optional[:class:`str`]
            Name of the official level.

        index: Optional[:class:`int`]
            Index (position) of the official level.

        client: Optional[:class:`~gd.Client`]
            Client to attach to the level.

        get_data: :class:`bool`
            Whether to attach data to the level. Default is ``True``.

        server_style: :class:`bool`
            Indicates if server-style of official song ID should be used.
            Set this to ``True`` in case of uploading level to the server. Defaults to ``False``.

        Raises
        ------
        :exc:`ValueError`
            No queries were given.

        :exc:`LookupError`
            Level was not found.

        Returns
        -------
        :class:`~gd.Level`
            Official level that was found.
        """
        if id is not None:
            official_level = iter(official_levels).get(level_id=id)

        elif name is not None:
            official_level = iter(official_levels).get(name=name)

        elif index is not None:
            try:
                official_level = official_levels[index]

            except (IndexError, ValueError, TypeError):
                official_level = None

        else:
            raise ValueError("Expected either of queries: level_id, name or index.")

        if official_level is None:
            raise LookupError("Could not find official level by given query.")

        return cast(OfficialLevel, official_level).into_level(
            client, get_data=get_data, server_style=server_style
        )

    @property
    def name(self) -> str:
        """:class:`str`: The name of the level."""
        return self.options.get("name", "Unnamed")

    @property
    def description(self) -> str:
        """:class:`str`: Description of the level."""
        return self.options.get("description", "")

    @property
    def version(self) -> int:
        """:class:`int`: Version of the level."""
        return self.options.get("version", 0)

    @property
    def downloads(self) -> int:
        """:class:`int`: Amount of the level's downloads."""
        return self.options.get("downloads", 0)

    @property
    def rating(self) -> int:
        """:class:`int`: Amount of the level's likes or dislikes."""
        return self.options.get("rating", 0)

    @property
    def score(self) -> int:
        """:class:`int`: Level's featured score."""
        return self.options.get("score", 0)

    @property
    def creator(self) -> User:
        """:class:`~gd.User`: Creator of the level."""
        return self.options.get("creator", User(client=self.client_unchecked))

    @property
    def song(self) -> Song:
        """:class:`~gd.Song`: Song used in the level."""
        return self.options.get("song", Song(client=self.client_unchecked))

    @property
    def difficulty(self) -> Union[DemonDifficulty, LevelDifficulty]:
        """Union[:class:`~gd.LevelDifficulty`, :class:`~gd.DemonDifficulty`]: Difficulty
        of the level.
        """
        difficulty = self.options.get("difficulty", -1)

        if self.is_demon():
            return DemonDifficulty.from_value(difficulty)

        else:
            return LevelDifficulty.from_value(difficulty)

    @property
    def password(self) -> Optional[int]:
        """Optional[:class:`int`]: The password to copy the level.
        See :meth:`~gd.Level.is_copyable`.
        """
        return self.options.get("password")

    def is_copyable(self) -> bool:
        """:class:`bool`: Indicates whether a level is copyable."""
        return bool(self.options.get("copyable"))

    @property
    def stars(self) -> int:
        """:class:`int`: Amount of stars the level has."""
        return self.options.get("stars", 0)

    @property
    def coins(self) -> int:
        """:class:`int`: Amount of coins in the level."""
        return self.options.get("coins", 0)

    @property
    def original_id(self) -> int:
        """:class:`int`: ID of the original level. (``0`` if is not a copy)"""
        return self.options.get("original_id", 0)

    @property
    def uploaded_at(self) -> Optional[datetime]:
        """Optional[:class:`~datetime.datetime`]:
        Timestamp representing when the level was uploaded.
        """
        return self.options.get("uploaded_at")

    @property
    def updated_at(self) -> Optional[datetime]:
        """Optional[:class:`~datetime.datetime`]:
        Timestamp representing when the level was last updated.
        """
        return self.options.get("updated_at")

    last_updated_at = updated_at

    @property
    def length(self) -> LevelLength:
        """:class:`~gd.LevelLength`: A type that represents length of the level."""
        return LevelLength.from_value(self.options.get("length", -1))

    @property
    def game_version(self) -> int:
        """:class:`int`: A version of the game required to play the level."""
        return self.options.get("game_version", 0)

    @property
    def requested_stars(self) -> int:
        """:class:`int`: Amount of stars creator of the level has requested."""
        return self.options.get("requested_stars", 0)

    @property
    def objects(self) -> int:
        """:class:`int`: Amount of objects the level has in data."""
        return object_count(self.data)

    @property
    def object_count(self) -> int:
        """:class:`int`: Amount of objects the level according to the servers."""
        return self.options.get("object_count", 0)

    @property
    def type(self) -> TimelyType:
        """:class:`~gd.TimelyType`: A type that shows whether a level is Daily/Weekly."""
        return TimelyType.from_value(self.options.get("type", 0))

    @property
    def timely_id(self) -> int:
        """:class:`int`: A number that represents current ID of the timely.
        Increments on new dailies/weeklies. If not timely, equals ``-1``.
        """
        return self.options.get("timely_id", -1)

    @property
    def cooldown(self) -> int:
        """:class:`int`: Represents a cooldown until next timely. If not timely, equals ``-1``."""
        return self.options.get("cooldown", -1)

    @property
    def editor_seconds(self) -> int:
        return self.options.get("editor_seconds", 0)

    @property
    def copies_seconds(self) -> int:
        return self.options.get("copies_seconds", 0)

    @property
    def editor_time(self) -> timedelta:
        return timedelta(seconds=self.editor_seconds)

    @property
    def copies_time(self) -> timedelta:
        return timedelta(seconds=self.copies_seconds)

    def get_unprocessed_data(self) -> str:
        return self.options.get("unprocessed_data", "")

    def set_unprocessed_data(self, unprocessed_data: str) -> None:
        self.options.update(unprocessed_data=unprocessed_data)

    unprocessed_data = property(get_unprocessed_data, set_unprocessed_data)

    @cache_by("unprocessed_data")
    def get_data(self) -> str:
        unprocessed_data = self.unprocessed_data

        if is_level_probably_decoded(unprocessed_data):
            return unprocessed_data

        else:
            return unzip_level_str(unprocessed_data)

    def set_data(self, data: str) -> None:
        if is_level_probably_decoded(data):
            self.unprocessed_data = zip_level_str(data)

        else:
            self.unprocessed_data = data

    data = property(get_data, set_data)

    def is_timely(self, timely_type: Optional[Union[int, str, TimelyType]] = None) -> bool:
        """:class:`bool`: Indicates whether a level is timely/daily/weekly."""
        if timely_type is None:
            return self.type is not TimelyType.NOT_TIMELY

        return self.type is TimelyType.from_value(timely_type)

    def is_current_timely(self, timely_type: Optional[Union[int, str, TimelyType]] = None) -> bool:
        """:class:`bool`: Indicates whether a level is current timely/daily/weekly level."""
        return self.is_timely(timely_type) and self.cooldown > 0

    def is_rated(self) -> bool:
        """:class:`bool`: Indicates if a level is rated (has stars)."""
        return self.stars > 0

    def was_unfeatured(self) -> bool:
        """:class:`bool`: Indicates if a level was featured, but got unfeatured."""
        return self.score < 0

    def is_featured(self) -> bool:
        """:class:`bool`: Indicates whether a level is featured."""
        return self.score > 0

    def is_epic(self) -> bool:
        """:class:`bool`: Indicates whether a level is epic."""
        return bool(self.options.get("epic"))

    def is_demon(self) -> bool:
        """:class:`bool`: Indicates whether a level is demon."""
        return bool(self.options.get("demon"))

    def is_auto(self) -> bool:
        """:class:`bool`: Indicates whether a level is auto."""
        return bool(self.options.get("auto"))

    def is_original(self) -> bool:
        """:class:`bool`: Indicates whether a level is original."""
        return not self.original_id

    def has_coins_verified(self) -> bool:
        """:class:`bool`: Indicates whether level's coins are verified."""
        return bool(self.options.get("verified_coins"))

    def has_low_detail_mode(self) -> bool:
        return bool(self.options.get("low_detail_mode"))

    def has_two_player(self) -> bool:
        return bool(self.options.get("two_player"))

    def open_editor(self) -> Editor:
        return Editor.load_from(self, "data")

    async def report(self) -> None:
        """Reports a level.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to report a level.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.report_level(self)

    async def upload(self, **kwargs) -> None:
        r"""Upload ``self``.

        Parameters
        ----------
        \*\*kwargs
            Arguments that :meth:`~gd.Client.upload_level` accepts.
            Defaults are properties of the level.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to upload the level.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        track_id, song_id = (0, self.song.id) if self.song.is_custom() else (self.song.id, 0)

        client = self.client_unchecked

        if client is None:
            client = kwargs.pop("from_client", None)

        if client is None:
            raise MissingAccess(
                "Could not find the client to upload level from. "
                "Either attach a client to this level or provide <from_client> parameter."
            )

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
        """Deletes a level.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to delete a level.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.delete_level(self)

    async def update_description(self, content: str) -> None:
        """Updates level description.

        Parameters
        ----------
        content: :class:`str`
            Content of the new description. If ``None`` or omitted, nothing is run.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to update level's description.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.update_level_description(self, content)

    async def rate(self, stars: int) -> None:
        """Sends level rating.

        Parameters
        ----------
        stars: :class:`int`
            Amount of stars to rate with.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to rate a level.
        """
        await self.client.rate_level(self, stars)

    async def rate_demon(
        self, demon_difficulty: Union[int, str, DemonDifficulty], as_mod: bool = False
    ) -> None:
        """Sends level demon rating.

        Parameters
        ----------
        demon_difficulty: Union[:class:`int`, :class:`str`, :class:`~gd.DemonDifficulty`]
            Demon difficulty to rate a level with.

        as_mod: :class:`bool`
            Whether to send a demon rating as moderator.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            If attempted to rate a level as moderator without required permissions.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """

        await self.client.rate_demon(self, demon_difficulty=demon_difficulty, as_mod=as_mod)

    async def send(self, stars: int, featured: bool) -> None:
        """Sends a level to Geometry Dash Developer and Administrator, *RobTop*.

        Parameters
        ----------
        stars: :class:`int`
            Amount of stars to send with.

        featured: :class:`bool`
            Whether to send for a feature, or for a rate.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Missing required moderator permissions.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.send_level(self, stars=stars, featured=featured)

    async def is_alive(self) -> bool:
        """Checks if a level is still on Geometry Dash servers.

        Returns
        -------
        :class:`bool`
            ``True`` if a level is still *alive*, and ``False`` otherwise.
            Also ``False`` if a client is not attached to the level.
        """
        try:
            await self.client.search_levels_on_page(query=self.id)

        except MissingAccess:
            return False

        return True

    async def update(self, *, get_data: bool = True) -> Optional["Level"]:
        """Refreshes a level. Returns ``None`` on fail.

        .. note::

            This function actually refreshes a level and its stats.
            No need to do funky stuff with its return.

        Returns
        -------
        :class:`~gd.Level`
            A newly fetched version. ``None`` if failed to fetch.
        """
        try:
            if self.type is TimelyType.DAILY:
                new = await self.client.get_daily()

            elif self.type is TimelyType.WEEKLY:
                new = await self.client.get_weekly()

            else:
                new = await self.client.get_level(self.id, get_data=get_data)

            if new.id != self.id:
                log.warning(
                    f"Level has changed: {self.name} ({self.id}) -> "
                    f"{new.name} ({new.id}). Updating to it..."
                )

        except MissingAccess:
            log.warning("Failed to update the level: %r. Most likely it was deleted.", self)
            return None

        self.options.update(new.options)

        return self

    refresh = update

    async def comment(self, content: str, percent: int = 0) -> Optional["Comment"]:
        """Posts a comment on a level.

        Parameters
        ----------
        content: :class:`str`
            Body of the comment to post.

        percent: :class:`int`
            Percentage to display. Default is ``0``.

            .. note::

                gd.py developers are not responsible for effects that changing this may cause.
                Set this parameter higher than 0 on your own risk.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to post a level comment.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        Optional[:class:`~gd.Comment`]
            Sent comment.
        """
        return await self.client.comment_level(self, content, percent)

    async def like(self) -> None:
        """Likes a level.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to like a level.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.like(self)

    async def dislike(self) -> None:
        """Dislikes a level.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to dislike a level.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.dislike(self)

    @awaitable_iterator
    def get_leaderboard(
        self, strategy: Union[int, str, LevelLeaderboardStrategy] = LevelLeaderboardStrategy.ALL,
    ) -> AsyncIterator[User]:
        """Retrieves the leaderboard of a level.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`~gd.LevelLeaderboardStrategy`]
            Strategy to apply when fetching.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to get leaderboard of the level.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        AsyncIterator[:class:`~gd.User`]
            A list of users.
        """
        return self.client.get_level_leaderboard(self, strategy=strategy)

    @awaitable_iterator
    def get_comments(
        self,
        strategy: Union[int, str, CommentStrategy] = CommentStrategy.RECENT,
        pages: Iterable[int] = ZERO_PAGE,
        amount: int = COMMENT_PAGE_SIZE,
        concurrent: bool = CONCURRENT,
    ) -> AsyncIterator["Comment"]:
        """Retrieves level comments.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`~gd.CommentStrategy`]
            A strategy to apply when searching.

        pages: Iterable[:class:`int`]
            Pages to search at. By default, only page ``0``.

        amount: :class:`int`
            Amount of comments to retrieve. Default is ``20``.
            For ``amount < 0``, ``1 << 31`` is added, allowing to fetch
            a theoretical limit of comments.

        concurrent: :class:`bool`
            Whether to fetch pages concurrently. ``True`` by default.

        Returns
        -------
        AsyncIterator[:class:`~gd.Comment`]
            Comments retrieved.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to fetch comments.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        return self.client.get_level_comments(
            level=self, strategy=strategy, pages=pages, amount=amount, concurrent=concurrent,
        )

    @awaitable_iterator
    def get_comments_on_page(
        self,
        strategy: Union[int, str, CommentStrategy] = CommentStrategy.RECENT,
        page: int = 0,
        amount: int = COMMENT_PAGE_SIZE,
    ) -> AsyncIterator["Comment"]:
        """Retrieves level comments.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`~gd.CommentStrategy`]
            A strategy to apply when searching.

        amount: :class:`int`
            Amount of comments to retrieve. Default is ``20``.
            For ``amount < 0``, ``1 << 31`` is added, allowing to fetch
            a theoretical limit of comments.

        Returns
        -------
        AsyncIterator[:class:`~gd.Comment`]
            Comments retrieved.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to fetch comments.

        :exc:`~gd.NothingFound`
            No comments were found.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        return self.client.get_level_comments_on_page(
            level=self, page=page, amount=amount, strategy=strategy
        )


@dataclass
class OfficialLevel:
    """Simple dataclass to hold information about official levels.
    Use :meth:`~gd.OfficialLevel.into_level` for converting to :class:`~gd.Level`.
    """

    level_id: int = attrib()
    song_id: int = attrib()
    name: str = attrib()
    stars: int = attrib()
    difficulty: str = attrib()
    coins: int = attrib()
    length: str = attrib()
    game_version: GameVersion = attrib()

    def is_auto(self) -> bool:
        """Check whether the official level is auto."""
        return "auto" in self.difficulty

    def is_demon(self) -> bool:
        """Check whether the official level is demon."""
        return "demon" in self.difficulty

    def get_song_id(self, server_style: bool = False) -> int:
        """Get correct song ID from ``self.song_id``.
        ``server_style`` indicates whether the song ID should match one on the server.
        """
        return self.song_id - 1 if server_style else self.song_id  # assume non-server by default

    def into_level(
        self,
        client: Optional["Client"] = None,
        get_data: bool = True,
        server_style: bool = False,
        cls: Type[Level] = Level,
    ) -> Level:
        """Convert :class:`~gd.OfficialLevel` dataclass into :class:`~gd.Level`.

        Parameters
        ----------
        client: Optional[:class:`~gd.Client`]
            Client to attach. ``None`` by default.

        get_data: :class:`bool`
            Whether to decode and attach level data. ``True`` by default.

        server_style: :class:`bool`
            Whether song ID should match one on the server.

        Returns
        -------
        :class:`~gd.Level`
            Level created from the dataclass.
        """
        global official_levels_data

        if self.is_demon():
            difficulty = DemonDifficulty.from_name(self.difficulty)

        else:
            difficulty = LevelDifficulty.from_name(self.difficulty)

        if get_data:
            if not official_levels_data and official_levels_path.exists():
                official_levels_data = json.loads(official_levels_path.read_text())

            unprocessed_data = official_levels_data.get(self.name, "")

        else:
            unprocessed_data = ""

        return cls(
            id=self.level_id,
            name=self.name,
            description=f"Official Level: {self.name}",
            unprocessed_data=unprocessed_data,
            version=1,
            creator=User(name="RobTop", id=16, account_id=71, client=client),
            song=Song.official(
                self.get_song_id(server_style), client=client, server_style=server_style
            ),
            downloads=0,
            game_version=self.game_version,
            rating=0,
            length=LevelLength.from_name(self.length),
            demon=self.is_demon(),
            stars=self.stars,
            score=1,
            auto=self.is_auto(),
            password=None,
            copyable=False,
            difficulty=difficulty,
            uploaded_at=None,
            updated_at=None,
            original_id=0,
            two_player=False,
            extra_string="",
            coins=self.coins,
            verified_coins=True,
            requested_stars=self.stars,
            low_detail_mode=False,
            epic=False,
            object_count=0,
            editor_seconds=0,
            copies_seconds=0,
            timely_id=-1,
            type=TimelyType.NOT_TIMELY,
            cooldown=-1,
            client=client,
        )


official_levels = (
    OfficialLevel(
        level_id=1,
        song_id=1,
        name="Stereo Madness",
        stars=1,
        difficulty="easy",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=2,
        song_id=2,
        name="Back On Track",
        stars=2,
        difficulty="easy",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=3,
        song_id=3,
        name="Polargeist",
        stars=3,
        difficulty="normal",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=4,
        song_id=4,
        name="Dry Out",
        stars=4,
        difficulty="normal",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=5,
        song_id=5,
        name="Base After Base",
        stars=5,
        difficulty="hard",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=6,
        song_id=6,
        name="Cant Let Go",
        stars=6,
        difficulty="hard",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=7,
        song_id=7,
        name="Jumper",
        stars=7,
        difficulty="harder",
        coins=3,
        length="long",
        game_version=GameVersion(1, 0),
    ),
    OfficialLevel(
        level_id=8,
        song_id=8,
        name="Time Machine",
        stars=8,
        difficulty="harder",
        coins=3,
        length="long",
        game_version=GameVersion(1, 1),
    ),
    OfficialLevel(
        level_id=9,
        song_id=9,
        name="Cycles",
        stars=9,
        difficulty="harder",
        coins=3,
        length="long",
        game_version=GameVersion(1, 2),
    ),
    OfficialLevel(
        level_id=10,
        song_id=10,
        name="xStep",
        stars=10,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(1, 3),
    ),
    OfficialLevel(
        level_id=11,
        song_id=11,
        name="Clutterfunk",
        stars=11,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(1, 4),
    ),
    OfficialLevel(
        level_id=12,
        song_id=12,
        name="Theory of Everything",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(1, 5),
    ),
    OfficialLevel(
        level_id=13,
        song_id=13,
        name="Electroman Adventures",
        stars=10,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(1, 6),
    ),
    OfficialLevel(
        level_id=14,
        song_id=14,
        name="Clubstep",
        stars=14,
        difficulty="easy_demon",
        coins=3,
        length="long",
        game_version=GameVersion(1, 6),
    ),
    OfficialLevel(
        level_id=15,
        song_id=15,
        name="Electrodynamix",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(1, 7),
    ),
    OfficialLevel(
        level_id=16,
        song_id=16,
        name="Hexagon Force",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(1, 8),
    ),
    OfficialLevel(
        level_id=17,
        song_id=17,
        name="Blast Processing",
        stars=10,
        difficulty="harder",
        coins=3,
        length="long",
        game_version=GameVersion(1, 9),
    ),
    OfficialLevel(
        level_id=18,
        song_id=18,
        name="Theory of Everything 2",
        stars=14,
        difficulty="easy_demon",
        coins=3,
        length="long",
        game_version=GameVersion(1, 9),
    ),
    OfficialLevel(
        level_id=19,
        song_id=19,
        name="Geometrical Dominator",
        stars=10,
        difficulty="harder",
        coins=3,
        length="long",
        game_version=GameVersion(2, 0),
    ),
    OfficialLevel(
        level_id=20,
        song_id=20,
        name="Deadlocked",
        stars=15,
        difficulty="medium_demon",
        coins=3,
        length="long",
        game_version=GameVersion(2, 0),
    ),
    OfficialLevel(
        level_id=21,
        song_id=21,
        name="Fingerdash",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=1001,
        song_id=22,
        name="The Seven Seas",
        stars=1,
        difficulty="easy",
        coins=3,
        length="long",
        game_version=GameVersion(2, 0),
    ),
    OfficialLevel(
        level_id=1002,
        song_id=23,
        name="Viking Arena",
        stars=2,
        difficulty="normal",
        coins=3,
        length="long",
        game_version=GameVersion(2, 0),
    ),
    OfficialLevel(
        level_id=1003,
        song_id=24,
        name="Airborne Robots",
        stars=3,
        difficulty="hard",
        coins=3,
        length="long",
        game_version=GameVersion(2, 0),
    ),
    OfficialLevel(
        level_id=2001,
        song_id=26,
        name="Payload",
        stars=2,
        difficulty="easy",
        coins=0,
        length="short",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2002,
        song_id=27,
        name="Beast Mode",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2003,
        song_id=28,
        name="Machina",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2004,
        song_id=29,
        name="Years",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2005,
        song_id=30,
        name="Frontlines",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2006,
        song_id=31,
        name="Space Pirates",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2007,
        song_id=32,
        name="Striker",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2008,
        song_id=33,
        name="Embers",
        stars=3,
        difficulty="normal",
        coins=0,
        length="short",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2009,
        song_id=34,
        name="Round 1",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=2010,
        song_id=35,
        name="Monster Dance Off",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=3001,
        song_id=25,
        name="The Challenge",
        stars=3,
        difficulty="hard",
        coins=0,
        length="short",
        game_version=GameVersion(2, 1),
    ),
    OfficialLevel(
        level_id=4001,
        song_id=36,
        name="Press Start",
        stars=4,
        difficulty="normal",
        coins=3,
        length="long",
        game_version=GameVersion(2, 2),
    ),
    OfficialLevel(
        level_id=4002,
        song_id=37,
        name="Nock Em",
        stars=6,
        difficulty="hard",
        coins=3,
        length="long",
        game_version=GameVersion(2, 2),
    ),
    OfficialLevel(
        level_id=4003,
        song_id=38,
        name="Power Trip",
        stars=8,
        difficulty="harder",
        coins=3,
        length="long",
        game_version=GameVersion(2, 2),
    ),
)
