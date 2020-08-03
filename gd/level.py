import json
from pathlib import Path

from attr import attrib, dataclass

from gd.logging import get_logger
from gd.typing import (
    Any,
    Client,
    Comment,
    Dict,
    Level,
    LevelRecord,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from gd.abstractentity import AbstractEntity
from gd.abstractuser import AbstractUser
from gd.song import Song

from gd.errors import MissingAccess, NothingFound

from gd.api.editor import Editor

from gd.utils.converter import Converter
from gd.utils.enums import (
    DemonDifficulty,
    LevelDifficulty,
    CommentStrategy,
    LevelLength,
    TimelyType,
    LevelLeaderboardStrategy,
)
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.search_utils import get
from gd.utils.text_tools import make_repr, object_split
from gd.utils.crypto.coders import Coder

official_levels_path = Path(__file__).parent / "official_levels.json"

if official_levels_path.exists():
    official_levels_data = json.loads(official_levels_path.read_text())

else:
    official_levels_data = {}

log = get_logger(__name__)


def excluding(*args: Tuple[Type[BaseException]]) -> Tuple[Type[BaseException]]:
    return args


DEFAULT_EXCLUDE: Tuple[Type[BaseException]] = excluding(NothingFound)
ZERO_STR = "0"


class Level(AbstractEntity):
    """Class that represents a Geometry Dash Level.
    This class is derived from :class:`.AbstractEntity`.
    """

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

    def __json__(self) -> Dict[str, Any]:
        return dict(
            super().__json__(),
            featured=self.is_featured(),
            was_unfeatured=self.was_unfeatured(),
            objects=self.objects,
        )

    @classmethod
    def official(
        cls,
        id: Optional[int] = None,
        name: Optional[str] = None,
        index: Optional[int] = None,
        client: Optional[Client] = None,
        get_data: bool = True,
        server_style: bool = False,
    ) -> Level:
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

        client: Optional[:class:`.Client`]
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
        :class:`.Level`
            Official level that was found.
        """
        if id is not None:
            official_level = get(official_levels, level_id=id)

        elif name is not None:
            official_level = get(official_levels, name=name)

        elif index is not None:
            try:
                official_level = official_levels[index]
            except (IndexError, TypeError):
                official_level = None

        else:
            raise ValueError("Expected either of queries: level_id, name or index.")

        if official_level is None:
            raise LookupError("Could not find official level by given query.")

        return official_level.into_level(client, get_data=get_data, server_style=server_style)

    @classmethod
    def from_data(
        cls,
        data: ExtDict,
        creator: Union[ExtDict, AbstractUser],
        song: Union[ExtDict, Song],
        client: Client,
    ) -> Level:
        if isinstance(creator, ExtDict):
            creator = AbstractUser(**creator, client=client)

        if isinstance(song, ExtDict):
            if any(key.isdigit() for key in song.keys()):
                song = Song.from_data(song, client=client)
            else:
                song = Song(**song, client=client)

        string = data.get(Index.LEVEL_PASS)

        if string is None:
            copyable, password = False, None
        else:
            if string == ZERO_STR:
                copyable, password = False, None
            else:
                try:
                    # decode password
                    password = Coder.decode(type="levelpass", string=string)
                except Exception:
                    # failed to get password
                    copyable, password = False, None
                else:
                    copyable = True

                    if not password:
                        password = None

                    else:
                        # password is in format 1XXXXXX
                        password = password[1:]
                        password = int(password) if password.isdigit() else None

        desc = Coder.do_base64(
            data.get(Index.LEVEL_DESCRIPTION, ""), encode=False, errors="replace"
        )

        level_data = data.get(Index.LEVEL_DATA, "")
        try:
            level_data = Coder.unzip(level_data)
        except Exception:  # conversion failed
            pass

        diff = data.getcast(Index.LEVEL_DIFFICULTY, 0, int)
        demon_diff = data.getcast(Index.LEVEL_DEMON_DIFFICULTY, 0, int)
        is_demon = bool(data.getcast(Index.LEVEL_IS_DEMON, 0, int))
        is_auto = bool(data.getcast(Index.LEVEL_IS_AUTO, 0, int))
        difficulty = Converter.convert_level_difficulty(
            diff=diff, demon_diff=demon_diff, is_demon=is_demon, is_auto=is_auto
        )

        return cls(
            id=data.getcast(Index.LEVEL_ID, 0, int),
            name=data.get(Index.LEVEL_NAME, "unknown"),
            description=desc,
            version=data.getcast(Index.LEVEL_VERSION, 0, int),
            creator=creator,
            song=song,
            data=level_data,
            password=password,
            copyable=copyable,
            is_demon=is_demon,
            is_auto=is_auto,
            low_detail_mode=bool(data.get(Index.LEVEL_HAS_LDM)),
            difficulty=difficulty,
            stars=data.getcast(Index.LEVEL_STARS, 0, int),
            coins=data.getcast(Index.LEVEL_COIN_COUNT, 0, int),
            verified_coins=bool(data.getcast(Index.LEVEL_COIN_VERIFIED, 0, int)),
            is_epic=bool(data.getcast(Index.LEVEL_IS_EPIC, 0, int)),
            original=data.getcast(Index.LEVEL_ORIGINAL, 0, int),
            downloads=data.getcast(Index.LEVEL_DOWNLOADS, 0, int),
            rating=data.getcast(Index.LEVEL_LIKES, 0, int),
            score=data.getcast(Index.LEVEL_FEATURED_SCORE, 0, int),
            uploaded_timestamp=data.get(Index.LEVEL_UPLOADED_TIMESTAMP, "unknown"),
            last_updated_timestamp=data.get(Index.LEVEL_LAST_UPDATED_TIMESTAMP, "unknown"),
            length=LevelLength.from_value(data.getcast(Index.LEVEL_LENGTH, 0, int)),
            game_version=data.getcast(Index.LEVEL_GAME_VERSION, 0, int),
            stars_requested=data.getcast(Index.LEVEL_REQUESTED_STARS, 0, int),
            object_count=data.getcast(Index.LEVEL_OBJECT_COUNT, 0, int),
            type=TimelyType.from_value(data.getcast(Index.LEVEL_TIMELY_TYPE, 0, int), 0),
            time_n=data.getcast(Index.LEVEL_TIMELY_INDEX, -1, int),
            cooldown=data.getcast(Index.LEVEL_TIMELY_COOLDOWN, -1, int),
            client=client,
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
    def creator(self) -> AbstractUser:
        """:class:`.AbstractUser`: Creator of the level."""
        return self.options.get("creator", AbstractUser(client=self.options.get("client")))

    @property
    def song(self) -> Song:
        """:class:`.Song`: Song used in the level."""
        return self.options.get("song", Song(client=self.options.get("client")))

    @property
    def difficulty(self) -> Union[DemonDifficulty, LevelDifficulty]:
        """Union[:class:`.LevelDifficulty`, :class:`.DemonDifficulty`]: Difficulty of the level."""
        difficulty = self.options.get("difficulty", -1)

        if self.is_demon():
            return DemonDifficulty.from_value(difficulty)

        else:
            return LevelDifficulty.from_value(difficulty)

    @property
    def password(self) -> Optional[int]:
        """Optional[:class:`int`]: The password to copy the level.
        See :meth:`.Level.is_copyable`.
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
        return self.options.get("original", 0)

    @property
    def uploaded_timestamp(self) -> str:
        """:class:`str`: A human-readable string representing how much time ago level was uploaded."""
        return self.options.get("uploaded_timestamp", "unknown")

    @property
    def last_updated_timestamp(self) -> str:
        """:class:`str`: A human-readable string showing how much time ago the last update was."""
        return self.options.get("last_updated_timestamp", "unknown")

    @property
    def length(self) -> LevelLength:
        """:class:`.LevelLength`: A type that represents length of the level."""
        return LevelLength.from_value(self.options.get("length", -1))

    @property
    def game_version(self) -> int:
        """:class:`int`: A version of the game required to play the level."""
        return self.options.get("game_version", 0)

    @property
    def requested_stars(self) -> int:
        """:class:`int`: Amount of stars creator of the level has requested."""
        return self.options.get("stars_requested", 0)

    @property
    def objects(self) -> int:
        """:class:`int`: Amount of objects the level has in data."""
        return len(object_split(self.data))

    @property
    def object_count(self) -> int:
        """:class:`int`: Amount of objects the level according to the servers."""
        return self.options.get("object_count", 0)

    @property
    def type(self) -> TimelyType:
        """:class:`.TimelyType`: A type that shows whether a level is Daily/Weekly."""
        return TimelyType.from_value(self.options.get("type", 0))

    @property
    def timely_index(self) -> int:
        """:class:`int`: A number that represents current index of the timely.
        Increments on new dailies/weeklies. If not timely, equals ``-1``.
        """
        return self.options.get("time_n", -1)

    @property
    def cooldown(self) -> int:
        """:class:`int`: Represents a cooldown until next timely. If not timely, equals ``-1``."""
        return self.options.get("cooldown", -1)

    @property
    def data(self) -> Union[bytes, str]:
        """Union[:class:`str`, :class:`bytes`]: Level data, represented as a stream."""
        return self.options.get("data", "")

    @data.setter
    def data(self, value: Union[bytes, str]) -> None:
        """Set ``self.data`` to ``value``."""
        self.options.update(data=value)

    def is_timely(self, daily_or_weekly: Optional[str] = None) -> bool:
        """:class:`bool`: Indicates whether a level is timely/daily/weekly.
        For instance, let's suppose a *level* is daily. Then, the behavior of this method is:
        ``level.is_timely() -> True`` and ``level.is_timely('daily') -> True`` but
        ``level.is_timely('weekly') -> False``."""
        if self.type is None:  # pragma: no cover
            return False

        if daily_or_weekly is None:
            return self.type.value > 0

        assert daily_or_weekly in ("daily", "weekly")

        return self.type.name.lower() == daily_or_weekly

    def is_rated(self) -> bool:
        """:class:`bool`: Indicates if a level is rated (has stars)."""
        return self.stars > 0

    def was_unfeatured(self) -> bool:
        """:class:`bool`: Indicates if a level was featured, but got unfeatured."""
        return self.score < 0

    def is_featured(self) -> bool:
        """:class:`bool`: Indicates whether a level is featured."""
        return self.score > 0  # not sure if this is the right way though

    def is_epic(self) -> bool:
        """:class:`bool`: Indicates whether a level is epic."""
        return bool(self.options.get("is_epic"))

    def is_demon(self) -> bool:
        """:class:`bool`: Indicates whether a level is demon."""
        return bool(self.options.get("is_demon"))

    def is_auto(self) -> bool:
        """:class:`bool`: Indicates whether a level is auto."""
        return bool(self.options.get("is_auto"))

    def is_original(self) -> bool:
        """:class:`bool`: Indicates whether a level is original."""
        return not self.original_id

    def has_coins_verified(self) -> bool:
        """:class:`bool`: Indicates whether level's coins are verified."""
        return bool(self.options.get("verified_coins"))

    def download(self) -> Union[bytes, str]:
        """Union[:class:`str`, :class:`bytes`]: Returns level data, represented as string."""
        return self.data

    def has_ldm(self) -> bool:
        return bool(self.options.get("low_detail_mode"))

    def open_editor(self) -> Editor:
        return Editor.launch(self, "data")

    async def report(self) -> None:
        """|coro|

        Reports a level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to report a level.
        """
        await self.client.report_level(self)

    async def upload(self, **kwargs) -> None:
        r"""|coro|

        Upload ``self``.

        Parameters
        ----------
        \*\*kwargs
            Arguments that :meth:`.Client.upload_level` accepts.
            Defaults are properties of the level.
        """
        track, song_id = (self.song.id, 0)

        if self.song.is_custom():
            track, song_id = song_id, track

        try:
            client = self.client
        except Exception:
            client = kwargs.pop("from_client", None)

            if client is None:
                raise MissingAccess(
                    "Could not find the client to upload level from. "
                    "Either attach a client to this level or provide <from_client> parameter."
                ) from None

        password = kwargs.pop("password", self.password)

        args = dict(
            name=self.name,
            id=self.id,
            version=self.version,
            length=abs(self.length.value),
            track=track,
            song_id=song_id,
            two_player=False,
            is_auto=self.is_auto(),
            original=self.original_id,
            objects=self.objects,
            coins=self.coins,
            star_amount=self.stars,
            unlisted=False,
            friends_only=False,
            ldm=False,
            password=password,
            copyable=self.is_copyable(),
            description=self.description,
            data=self.data,
        )

        args.update(kwargs)

        uploaded = await client.upload_level(**args)

        self.options = uploaded.options

    async def delete(self) -> None:
        """|coro|

        Deletes a level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a level.
        """
        await self.client.delete_level(self)

    async def update_description(self, content: Optional[str] = None) -> None:
        """|coro|

        Updates level description.

        Parameters
        ----------
        content: :class:`str`
            Content of the new description. If ``None`` or omitted, nothing is run.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to update level's description.
        """
        if content is None:
            return

        await self.client.update_level_description(self, content)

    async def rate(self, stars: int = 1) -> None:
        """|coro|

        Sends level rating.

        Parameters
        ----------
        stars: :class:`int`
            Amount of stars to rate with.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to rate a level.
        """
        await self.client.rate_level(self, stars)

    async def rate_demon(
        self, demon_difficulty: Union[int, str, DemonDifficulty] = 1, as_mod: bool = False
    ) -> None:
        """|coro|

        Sends level demon rating.

        Parameters
        ----------
        demon_difficulty: Union[:class:`int`, :class:`str`, :class:`.DemonDifficulty`]
            Demon difficulty to rate a level with.

        as_mod: :class:`bool`
            Whether to send a demon rating as moderator.

        Raises
        ------
        :exc:`.MissingAccess`
            If attempted to rate a level as moderator without required permissions.
        """

        await self.client.rate_demon(self, demon_difficulty=demon_difficulty, as_mod=as_mod)

    async def send(self, stars: int = 1, featured: bool = True) -> None:
        """|coro|

        Sends a level to Geometry Dash Developer and Administrator, *RobTop*.

        Parameters
        ----------
        stars: :class:`int`
            Amount of stars to send with.

        featured: :class:`bool`
            Whether to send to feature, or to simply rate.

        Raises
        ------
        :exc:`.MissingAccess`
            Missing required moderator permissions.
        """
        await self.client.send_level(self, stars=stars, featured=featured)

    async def is_alive(self) -> bool:
        """|coro|

        Checks if a level is still on Geometry Dash servers.

        Returns
        -------
        :class:`bool`
            ``True`` if a level is still *alive*, and ``False`` otherwise.
            Also ``False`` if a client is not attached to the level.s
        """
        try:
            await self.client.search_levels_on_page(query=str(self.id))

        except MissingAccess:
            return False

        return True

    async def refresh(self) -> Optional[Level]:
        """|coro|

        Refreshes a level. Returns ``None`` on fail.

        .. note::

            This function actually refreshes a level and its stats.
            No need to do funky stuff with its return.

        Returns
        -------
        :class:`.Level`
            A newly fetched version. ``None`` if failed to fetch.
        """
        try:
            if self.is_timely():
                async_func = getattr(self.client, "get_" + self.type.name.lower())
                new_ver = await async_func()

                if new_ver.id != self.id:
                    log.warning(
                        f"There is a new {self.type.title} Level: {new_ver!r}. Updating to it..."
                    )

            else:
                new_ver = await self.client.get_level(self.id)

        except MissingAccess:
            return log.warning("Failed to refresh level: %r. Most likely it was deleted.", self)

        self.options = new_ver.options

        return self

    async def comment(self, content: str, percentage: int = 0) -> Optional[Comment]:
        """|coro|

        Posts a comment on a level.

        Parameters
        ----------
        content: :class:`str`
            Body of the comment to post.

        percentage: :class:`int`
            Percentage to display. Default is ``0``.

            .. note::

                gd.py developers are not responsible for effects that changing this may cause.
                Set this parameter higher than 0 on your own risk.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to post a level comment.

        Returns
        -------
        Optional[:class:`.Comment`]
            Sent comment.
        """
        return await self.client.comment_level(self, content, percentage)

    async def like(self) -> None:
        """|coro|

        Likes a level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to like a level.
        """
        await self.client.like(self)

    async def dislike(self) -> None:
        """|coro|

        Dislikes a level.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to dislike a level.
        """
        await self.client.dislike(self)

    async def get_leaderboard(
        self, strategy: Union[int, str, LevelLeaderboardStrategy] = 0
    ) -> List[LevelRecord]:
        """|coro|

        Retrieves the leaderboard of a level.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`.LevelLeaderboardStrategy`]
            A strategy to apply.

        Returns
        -------
        List[:class:`.LevelRecord`]
            A list of user-like objects.
        """
        return await self.client.get_level_leaderboard(self, strategy=strategy)

    async def get_comments(
        self,
        strategy: Union[int, str, CommentStrategy] = 0,
        amount: int = 20,
        exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE,
    ) -> List[Comment]:
        """|coro|

        Retrieves level comments.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            A strategy to apply when searching.

        amount: :class:`int`
            Amount of comments to retrieve. Default is ``20``.
            For ``amount < 0``, ``2 ** 31`` is added, allowing to fetch
            a theoretical limit of comments.

        exclude: Tuple[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.Comment`]
            List of comments retrieved.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to fetch comments.

        :exc:`.NothingFound`
            No comments were found.
        """
        return await self.client.get_level_comments(
            self, strategy=strategy, amount=amount, exclude=exclude
        )


@dataclass
class OfficialLevel:
    level_id: int = attrib(kw_only=True)
    song_id: int = attrib(kw_only=True)
    name: str = attrib(kw_only=True)
    stars: int = attrib(kw_only=True)
    difficulty: str = attrib(kw_only=True)
    coins: int = attrib(kw_only=True)
    length: str = attrib(kw_only=True)

    def is_auto(self) -> bool:
        return "auto" in self.difficulty

    def is_demon(self) -> bool:
        return "demon" in self.difficulty

    def get_song_id(self, server_style: bool = False) -> int:
        return self.song_id - 1 if server_style else self.song_id  # assume non-server by default

    def into_level(
        self, client: Optional[Client] = None, get_data: bool = True, server_style: bool = False,
    ) -> Level:
        if self.is_demon():
            difficulty = DemonDifficulty.from_name(self.difficulty)
        else:
            difficulty = LevelDifficulty.from_name(self.difficulty)

        if get_data:
            data = official_levels_data.get(self.name, "")

            if data:
                data = Coder.unzip(data)

        else:
            data = ""

        return Level(
            id=self.level_id,
            name=self.name,
            description=f"Official Level: {self.name}",
            version=1,
            creator=AbstractUser(name="RobTop", id=16, account_id=71, client=client),
            song=Song.official(
                self.get_song_id(server_style), client=client, server_style=server_style
            ),
            data=data,
            password=None,
            copyable=False,
            is_demon=self.is_demon(),
            is_auto=self.is_auto(),
            difficulty=difficulty,
            stars=self.stars,
            coins=self.coins,
            verified_coins=True,
            is_epic=False,
            original=True,
            low_detail_mode=False,
            downloads=0,
            rating=0,
            score=1,
            uploaded_timestamp="unknown",
            last_updated_timestamp="unknown",
            length=LevelLength.from_name(self.length),
            stars_requested=self.stars,
            object_count=0,
            type=TimelyType.from_value(0),
            time_n=-1,
            cooldown=-1,
            client=client,
        )


official_levels = [
    OfficialLevel(
        level_id=1,
        song_id=1,
        name="Stereo Madness",
        stars=1,
        difficulty="easy",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=2,
        song_id=2,
        name="Back On Track",
        stars=2,
        difficulty="easy",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=3,
        song_id=3,
        name="Polargeist",
        stars=3,
        difficulty="normal",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=4, song_id=4, name="Dry Out", stars=4, difficulty="normal", coins=3, length="long",
    ),
    OfficialLevel(
        level_id=5,
        song_id=5,
        name="Base After Base",
        stars=5,
        difficulty="hard",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=6,
        song_id=6,
        name="Cant Let Go",
        stars=6,
        difficulty="hard",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=7, song_id=7, name="Jumper", stars=7, difficulty="harder", coins=3, length="long",
    ),
    OfficialLevel(
        level_id=8,
        song_id=8,
        name="Time Machine",
        stars=8,
        difficulty="harder",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=9, song_id=9, name="Cycles", stars=9, difficulty="harder", coins=3, length="long",
    ),
    OfficialLevel(
        level_id=10,
        song_id=10,
        name="xStep",
        stars=10,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=11,
        song_id=11,
        name="Clutterfunk",
        stars=11,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=12,
        song_id=12,
        name="Theory of Everything",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=13,
        song_id=13,
        name="Electroman Adventures",
        stars=10,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=14,
        song_id=14,
        name="Clubstep",
        stars=14,
        difficulty="easy_demon",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=15,
        song_id=15,
        name="Electrodynamix",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=16,
        song_id=16,
        name="Hexagon Force",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=17,
        song_id=17,
        name="Blast Processing",
        stars=10,
        difficulty="harder",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=18,
        song_id=18,
        name="Theory of Everything 2",
        stars=14,
        difficulty="easy_demon",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=19,
        song_id=19,
        name="Geometrical Dominator",
        stars=10,
        difficulty="harder",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=20,
        song_id=20,
        name="Deadlocked",
        stars=15,
        difficulty="medium_demon",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=21,
        song_id=21,
        name="Fingerdash",
        stars=12,
        difficulty="insane",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=1001,
        song_id=22,
        name="The Seven Seas",
        stars=1,
        difficulty="easy",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=1002,
        song_id=23,
        name="Viking Arena",
        stars=2,
        difficulty="normal",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=1003,
        song_id=24,
        name="Airborne Robots",
        stars=3,
        difficulty="hard",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=2001,
        song_id=26,
        name="Payload",
        stars=2,
        difficulty="easy",
        coins=0,
        length="short",
    ),
    OfficialLevel(
        level_id=2002,
        song_id=27,
        name="Beast Mode",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2003,
        song_id=28,
        name="Machina",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2004,
        song_id=29,
        name="Years",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2005,
        song_id=30,
        name="Frontlines",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2006,
        song_id=31,
        name="Space Pirates",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2007,
        song_id=32,
        name="Striker",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2008,
        song_id=33,
        name="Embers",
        stars=3,
        difficulty="normal",
        coins=0,
        length="short",
    ),
    OfficialLevel(
        level_id=2009,
        song_id=34,
        name="Round 1",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=2010,
        song_id=35,
        name="Monster Dance Off",
        stars=3,
        difficulty="normal",
        coins=0,
        length="medium",
    ),
    OfficialLevel(
        level_id=3001,
        song_id=25,
        name="The Challenge",
        stars=3,
        difficulty="hard",
        coins=0,
        length="short",
    ),
    OfficialLevel(
        level_id=4001,
        song_id=36,
        name="Press Start",
        stars=4,
        difficulty="normal",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=4002,
        song_id=37,
        name="Nock Em",
        stars=6,
        difficulty="hard",
        coins=3,
        length="long",
    ),
    OfficialLevel(
        level_id=4003,
        song_id=38,
        name="Power Trip",
        stars=8,
        difficulty="harder",
        coins=3,
        length="long",
    ),
]
