import asyncio

from gd.abstractuser import AbstractUser, LevelRecord
from gd.comment import Comment
from gd.errors import ClientException, NothingFound
from gd.friend_request import FriendRequest
from gd.level import Level
from gd.level_packs import Gauntlet, MapPack
from gd.logging import get_logger
from gd.message import Message
from gd.rewards import Chest, Quest
from gd.session import Session
from gd.song import ArtistInfo, Author, Song
from gd.typing import (
    Any,
    Client,
    Coroutine,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)
from gd.user import User, UserStats

from gd.events.listener import (
    TimelyLevelListener,
    RateLevelListener,
    MessageOrRequestListener,
    LevelCommentListener,
)

from gd.utils.converter import Converter
from gd.utils.decorators import check_logged, impl_sync
from gd.utils.enums import (
    CommentPolicyType,
    CommentStrategy,
    DemonDifficulty,
    FriendRequestPolicyType,
    IconType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    RewardType,
    MessagePolicyType,
)
from gd.utils.filters import Filters
from gd.utils.http_request import HTTPClient
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.save_parser import Save
from gd.utils.text_tools import make_repr

from gd.utils.crypto.coders import Coder

from gd import api, utils

log = get_logger(__name__)


def excluding(*args: Tuple[Type[BaseException]]) -> Tuple[Type[BaseException]]:
    return args


DEFAULT_EXCLUDE: Tuple[Type[BaseException]] = excluding(NothingFound)
DAILY, WEEKLY = -1, -2


def figure_type_and_special(item: Union[Comment, Level]) -> Optional[Tuple[int, int]]:
    # figure out typeid and "special" value for given item.
    # returns a pair: (typeid, special)
    if isinstance(item, Level):
        return 1, 0

    elif isinstance(item, Comment):
        if not item.type.value:
            return 2, item.level_id
        else:
            return 3, item.id

    else:
        return  # if we are here, that means invalid entity was provided.


def construct_levels(
    lvdata: Iterable[ExtDict], cdata: Iterable[ExtDict], sdata: Iterable[ExtDict], client: Client
) -> List[Level]:
    creators = list(AbstractUser(**c, client=client) for c in cdata)
    songs = list(Song.from_data(s, client=client) for s in sdata)
    levels = []

    for data in lvdata:
        song = utils.get(songs, id=data.getcast(Index.LEVEL_SONG_ID, 0, int))
        if song is None:
            song = Song(
                **Converter.to_normal_song(data.getcast(Index.LEVEL_AUDIO_TRACK, 0, int)),
                client=client,
            )

        creator_id = data.getcast(Index.LEVEL_CREATOR_ID, 0, int)
        creator = utils.get(creators, id=creator_id)
        if creator is None:
            creator = AbstractUser(id=creator_id, name="unknown", account_id=0, client=client)

        levels.append(Level.from_data(data, creator, song, client=client))

    return levels


async def is_alive_mock(level: Level) -> bool:
    # mock Level's is_alive method if the level was deleted.
    return False


@impl_sync
class Client:
    r"""A main class in the gd.py library, used for interacting with the servers of Geometry Dash.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used
        via :func:`.utils.acquire_loop`.

    load_after_post: :class:`bool`
        Whether to load comments/messages/requests after sending them.

        .. note::

            Defaults to ``True``, in which case the following method calls will return objects:

            - :meth:`.Client.send_message`;
            - :meth:`.Client.send_friend_request`;
            - :meth:`.Client.comment_level`;
            - :meth:`.Client.post_comment`.

            Otherwise, if ``False`` or not found (extremely rarely), these methods will return ``None``.

    \*\*http_args
        Arguments to pass to :class:`.HTTPClient` constructor.

    Attributes
    ----------
    account_id: :class:`int`
        Account ID of the client. If not logged in, defaults to ``0``.
    id: :class:`int`
        ID (Player ID) of the client. If not logged in, defaults to ``0``.
    name: :class:`str`
        Name of the client. If not logged in, default is ``None``.
    password: :class:`str`
        Password of the client. ``None`` if not logged in.
    encodedpass: :class:`str`
        Encoded Password of the client. ``None`` on init as well.
    db: Optional[:class:`.api.Database`]
        Database/Save API. If not loaded, has empty parts inside.
    save: :class:`.Save`
        This is a namedtuple with format ``(completed, followed)``.
        Contains empty lists if not loaded.
    """

    def __init__(
        self,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        load_after_post: bool = True,
        **http_args,
    ) -> None:
        if loop is None:
            loop = utils.acquire_loop()

        self.session = Session(**http_args)
        self.load_after_post = load_after_post
        self.listeners = list()
        self.loop = loop
        self._set_to_defaults()

    def __repr__(self) -> str:
        info = {
            "is_logged": self.is_logged(),
            "account_id": self.account_id,
            "id": self.id,
            "name": self.name,
            "password": "...",
        }
        return make_repr(self, info)

    def _json(self) -> Dict[str, Optional[Union[int, str]]]:  # pragma: no cover
        return dict(
            account_id=self.account_id,
            id=self.id,
            name=self.name,
            password=None,  # for safety reasons
        )

    def _set_to_defaults(self) -> None:
        self.save = Save(completed=list(), followed=list())
        self.db = api.Database()
        self.account_id = 0
        self.id = 0
        self.name = None
        self.password = None
        self.encodedpass = None

    def _upd(self, attr: str, value: Any) -> None:  # pragma: no cover
        setattr(self, attr, value)
        # update encodedpass if password was updated
        if attr == "password":
            self.encodedpass = Coder.encode(type="accountpass", string=self.password)

    def edit(self, **attrs) -> Client:
        """Update attributes given by ``attrs`` of ``self``.

        This could be used to manually set credentials, for example:

        .. code-block:: python3

            client = gd.Client()
            client.edit(name='NeKitDS', id=17876467, account_id=5509312, password='secret')
        """
        for attr, value in attrs.items():
            self._upd(attr, value)
        return self

    @property
    def http(self) -> HTTPClient:
        """:class:`.HTTPClient`: HTTP Client bound to that Client. Same as ``self.session.http``."""
        return self.session.http

    def is_logged(self) -> bool:
        """:class:`bool`: Indicates whether the Client is logged in."""
        checks = (
            self.name is not None,
            self.password is not None,
            self.account_id > 0,
            self.id > 0,
        )
        return all(checks)

    async def ping_server(self) -> float:
        """|coro|

        Pings ``boomlings.com/database`` and returns the time taken.

        Returns
        -------
        :class:`float`
            Server ping, in milliseconds.
        """
        return await self.session.ping_server("http://boomlings.com/database/")

    async def get_artist_info(self, song_id: int = 0) -> ArtistInfo:
        """|coro|

        Retrieves artist info about for a song with a particular ID.

        Parameters
        ----------
        song_id: :class:`int`
            An ID of the song whose info to fetch.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to fetch the song info.

        Returns
        -------
        :class:`.ArtistInfo`
            Info regarding the artist.
        """
        data = await self.session.test_song(song_id)
        return ArtistInfo(**data, client=self)

    async def get_song(self, song_id: int = 0) -> Song:
        """|coro|

        Fetches a song from Geometry Dash server.

        Parameters
        ----------
        song_id: :class:`int`
            An ID of the song to fetch.

        Raises
        ------
        :exc:`.MissingAccess`
            Song under given ID was not found or does not exist.

        :exc:`.SongRestrictedForUsage`
            Song was not allowed to use.

        Returns
        -------
        :class:`.Song`
            The song from the ID.
        """
        data = await self.session.get_song(song_id)
        return Song.from_data(data, client=self)

    async def get_ng_song(self, song_id: int = 0) -> Song:
        """|coro|

        Fetches a song from Newgrounds.

        This function is in most cases might be slower than :meth:`.Client.get_song`,
        but it does not raise errors if a song is banned on GD Server.

        Parameters
        ----------
        song_id: :class:`int`
            An ID of the song to fetch.

        Raises
        ------
        :exc:`.MissingAccess`
            Requested song is deleted from Newgrounds or does not exist.

        Returns
        -------
        :class:`.Song`
            The song found under given ID.
        """
        data = await self.session.get_ng_song(song_id)
        return Song(**data, client=self)

    async def search_page_songs(self, query: str, page: int = 0) -> List[Song]:
        """|coro|

        Search for songs on Newgrounds.

        Parameters
        ----------
        query: :class:`str`
            Query to search for.

        page: :class:`int`
            Page to look songs on.

        Returns
        -------
        List[:class:`.Song`]
            A list of Songs, containing attributes ``id``, ``name`` and ``author``.
        """
        data = await self.session.search_page_songs(query=query, page=page)
        return utils.unique(Song(**part, client=self) for part in data)

    async def search_songs(self, query: str, pages: Iterable[int] = range(10)) -> List[Song]:
        """|coro|

        Search for songs on Newgrounds.

        Parameters
        ----------
        query: :class:`str`
            Query to search for.

        pages: Iterable[:class:`int`]
            Pages to look songs on.

        Returns
        -------
        List[:class:`.Song`]
            A list of Songs, containing attributes ``id``, ``name`` and ``author``.
        """
        data = await self.session.search_songs(query=query, pages=pages)
        return utils.unique(Song(**part, client=self) for part in data)

    async def search_page_users(self, query: str, page: int = 0) -> List[Author]:
        """|coro|

        Search for users on Newgrounds.

        Parameters
        ----------
        query: :class:`str`
            Query to search for.

        page: :class:`int`
            Page to look users on.

        Returns
        -------
        List[:class:`.Author`]
            A list of Authors, containing attributes ``name`` and ``link``.
        """
        data = await self.session.search_page_users(query=query, page=page)
        return utils.unique(Author(**part, client=self) for part in data)

    async def search_users(self, query: str, pages: Iterable[int] = range(10)) -> List[Author]:
        """|coro|

        Search for users on Newgrounds.

        Parameters
        ----------
        query: :class:`str`
            Query to search for.

        pages: Iterable[:class:`int`]
            Pages to look users on.

        Returns
        -------
        List[:class:`.Author`]
            A list of Authors, containing attributes ``name`` and ``link``.
        """
        data = await self.session.search_users(query=query, pages=pages)
        return utils.unique(Author(**part, client=self) for part in data)

    async def get_page_user_songs(self, user: Union[str, Author], page: int = 0) -> List[Song]:
        """|coro|

        Search for songs by a user on Newgrounds.

        Parameters
        ----------
        query: :class:`str`
            Query to search for.

        page: :class:`int`
            Page to look songs on.

        Returns
        -------
        List[:class:`.Song`]
            A list of Songs, containing attributes ``id``, ``name`` and ``author``.
        """
        data = await self.session.get_page_user_songs(user, page=page)
        return utils.unique(Song(**part, client=self) for part in data)

    async def get_user_songs(
        self, user: Union[str, Author], pages: Iterable[int] = range(10)
    ) -> List[Song]:
        """|coro|

        Search for songs by a user on Newgrounds.

        Parameters
        ----------
        query: :class:`str`
            Query to search for.

        pages: Iterable[:class:`int`]
            Page to look songs on.

        Returns
        -------
        List[:class:`.Song`]
            A list of Songs, containing attributes ``id``, ``name`` and ``author``.
        """
        name = user.name if isinstance(user, Author) else user

        data = await self.session.get_user_songs(name, pages=pages)

        return list(Song(**part, client=self) for part in data)

    async def get_user(self, account_id: int = 0) -> User:
        """|coro|

        Gets a user from Geometry Dash server.

        Parameters
        ----------
        account_id: :class:`int`
            An account ID of the user to fetch.

        Raises
        ------
        :exc:`.MissingAccess`
            User with given account ID was not found.

        Returns
        -------
        :class:`.User`
            The user from the ID.
        """
        data = await self.session.get_user(account_id, return_only_stats=False)
        return User.from_data(data, client=self)

    async def fetch_user(
        self, account_id: int = 0, *, stats: bool = False
    ) -> Union[AbstractUser, UserStats]:
        """|coro|

        This is almost like :meth:`.Client.get_user`, except that it returns
        either :class:`.UserStats` or :class:`.AbstractUser` object.

        Parameters
        ----------
        account_id: :class:`int`
            An account ID of the user to fetch stats of.

        stats: :class:`bool`
            Whether to return :class:`.UserStats` or :class:`.AbstractUser`.
            By default returns :class:`.AbstractUser`.

        Raises
        ------
        :exc:`.MissingAccess`
            User with given account ID was not found, so fetching stats failed or user can not be returned.

        Returns
        -------
        Union[:class:`.UserStats`, :class:`.AbstractUser`]
            Abstract user or User stats from the ID. (if ID != -1)
        """
        data = await self.session.get_user(account_id, return_only_stats=True)
        user_stats = UserStats.from_data(data, client=self)
        # return UserStats if needed, and AbstractUser otherwise.
        return user_stats if stats else user_stats.as_user()

    async def search_user(self, query: Union[int, str]) -> User:
        """|coro|

        Searches for a user on Geometry Dash servers.

        Parameters
        ----------
        query: Union[:class:`int`, :class:`str`]
            A query to search for user with. Either Player ID or Name.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing was found.

        Returns
        -------
        Union[:class:`.User`]
            A User found when searching with the query.
        """
        data = await self.session.search_user(query, return_abstract=False)
        return User.from_data(data, client=self)

    async def find_user(self, query: Union[int, str]) -> AbstractUser:
        """|coro|

        Fetches a user on Geometry Dash servers by given query.

        Works almost like :meth:`.Client.search_user`, except the fact that
        it returns :class:`.AbstractUser`.

        Parameters
        ----------
        query: Union[:class:`int`, :class:`str`]
            A query to search for user with.

        Raises
        ------
        :exc:`.MissingAccess`
            No user was found.

        Returns
        -------
        Union[:class:`.AbstractUser`]
            An AbstractUser corresponding to the query.
        """
        data = await self.session.search_user(query, return_abstract=True)
        return AbstractUser.from_data(data, client=self)

    async def get_daily(self) -> Level:
        """|coro|

        Gets current daily level.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing found or invalid response was received.
        Returns
        -------
        :class:`.Level`
            Current daily level.
        """
        return await self.get_level(DAILY)

    async def get_weekly(self) -> Level:
        """|coro|

        Gets current weekly demon.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing found or invalid response was received.
        Returns
        -------
        :class:`.Level`
            Current weekly demon.
        """
        return await self.get_level(WEEKLY)

    async def get_level(self, level_id: int = 0, get_data: bool = True) -> Level:
        """|coro|

        Fetches a level from Geometry Dash servers.

        Parameters
        ----------
        level_id: :class:`int`
            An ID of the level to fetch.

            .. note::

                If the given ID is *n*, and *0 > n >= -2*,
                this function will search for daily/weekly levels, however,
                it is not recommended to use since it can cause confusion.
                Use :meth:`.Client.get_daily` and :meth:`.Client.get_weekly`
                for better understanding.

        get_data: :class:`bool`
            Whether to download the level data or not.

        Raises
        ------
        :exc:`.MissingAccess`
            Level with given ID was not found.

        Returns
        -------
        :class:`.Level`
            The level corresponding to given id.
        """
        if get_data:
            level_data, creator_data, song_data = await self.session.get_level_info(level_id)
        else:
            return (await self.search_levels_on_page(query=level_id))[0]

        return Level.from_data(level_data, creator_data, song_data, client=self)

    async def get_many_levels(self, *level_ids: Sequence[int]) -> List[Level]:
        r"""|coro|

        Fetches many levels.

        Parameters
        ----------
        \*level_ids: Sequence[:class:`int`]
            IDs of levels to fetch. This function returns all the levels that it is able to find.

            Example:

            .. code-block:: python3

                await client.get_many_levels(30029017, 44622744)

        Raises
        ------
        :exc:`.MissingAccess`
            Levels were not found.

        Returns
        -------
        List[:class:`.Level`]
            A list of all levels found.
        """
        filters = Filters.setup_search_many()
        query = ",".join(map(str, level_ids))

        return await self.search_levels_on_page(query=query, filters=filters)

    async def get_gauntlets(self) -> List[Gauntlet]:
        """|coro|

        Fetches *The Lost Gauntlets*.

        Returns
        -------
        List[:class:`.Gauntlet`]
            All gauntlets retrieved, as list.
        """
        data = await self.session.get_gauntlets()
        return list(Gauntlet.from_data(part, client=self) for part in data)

    async def get_page_map_packs(
        self, page: int = 0, *, exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE
    ) -> List[MapPack]:
        """|coro|

        Fetches map packs on given page.

        Parameters
        ----------
        page: :class:`int`
            Page to look for map packs on.

        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.MapPack`]
            List of map packs retrieved.

        Raises
        ------
        :exc:`.NothingFound`
            No map packs were found at the given page.
        """
        data = await self.session.get_page_map_packs(page=page, exclude=exclude)
        return list(MapPack.from_data(part, client=self) for part in data)

    async def get_map_packs(self, pages: Optional[Iterable[int]] = range(10)) -> List[MapPack]:
        """|coro|

        Gets map packs on given ``pages``.

        Parameters
        ----------
        pages: Iterable[:class:`int`]
            Pages to search map packs on.

        Returns
        -------
        List[:class:`.MapPack`]
            List of map packs found.
        """
        data = await self.session.get_map_packs(pages=pages)
        return list(MapPack.from_data(part, client=self) for part in data)

    async def unsafe_login(self, user: str, password: str) -> None:
        """|coro|

        Login into account, without validating credentials.

        Parameters
        ----------
        user: :class:`str`
            A username of the account to log into.

        password: :class:`str`
            A password of the account to log into.

        Raises
        ------
        :exc:`.MissingAccess`
            Could not find account by given ``user``.
        """
        self_user = await self.find_user(user)
        self.edit(name=user, password=password, account_id=self_user.account_id, id=self_user.id)
        log.info("Logged in? as %r, with password %r.", user, password)

    async def login(self, user: str, password: str) -> None:
        """|coro|

        Tries to login with given parameters.

        Parameters
        ----------
        user: :class:`str`
            A username of the account to log into.

        password: :class:`str`
            A password of the account to log into.

        Raises
        ------
        :exc:`.LoginFailure`
            Given account credentials are not correct.
        """
        account_id, player_id = await self.session.login(user=user, password=password)
        self.edit(name=user, password=password, account_id=account_id, id=player_id)

        log.info("Logged in as %r, with password %r.", user, password)

    @check_logged
    async def upload_level(
        self,
        name: str = "Unnamed",
        id: int = 0,
        version: int = 1,
        length: Union[int, str, LevelLength] = 0,
        track: int = 0,
        song_id: int = 0,
        is_auto: bool = False,
        original: int = 0,
        two_player: bool = False,
        objects: Optional[int] = None,
        coins: int = 0,
        star_amount: int = 0,
        unlist: bool = False,
        ldm: bool = False,
        password: Optional[Union[int, str]] = None,
        copyable: bool = False,
        data: Union[bytes, str] = "",
        description: str = "",
        *,
        load: bool = True,
    ) -> Level:
        """|coro|

        Upload a level.

        Parameters
        ----------
        name: :class:`str`
            A name of the level.
        id: :class:`int`
            An ID of the level. ``0`` if uploading a new level,
            non-zero when attempting to update already existing level.
        version: :class:`int`
            A version of the level.
        length: Union[:class:`int`, :class:`str`, :class:`.LevelLength`]
            A length of the level. See :class:`.LevelLength` for more info.
        track: :class:`int`
            A normal track to set, e.g. ``0 - Stereo Madness, 1 - Back on Track, ...``.
        song_id: :class:`int`
            An ID of the custom song to set.
        is_auto: :class:`bool`
            Indicates if the level is auto.
        original: :class:`int`
            An ID of the original level.
        two_player: :class:`bool`
            Indicates whether the level has enabled Two Player mode.
        objects: :class:`int`
            The amount of objects in the level. If not provided, the amount
            is being calculated from the ``data`` parameter.
        coins: :class:`int`
            An amount of coins the level has.
        star_amount: :class:`int`
            The amount of stars to request.
        unlist: :class:`bool`
            Indicates whether the level should be unlisted.
        ldm: :class:`bool`
            Indicates if the level has LDM mode.
        password: Union[:class:`int`, :class:`str`]
            The password to apply.
            Either a natural number or a string representing a natural number.
            If ``None``, depending on what ``copyable`` is,
            either indicates whether a level is free to copy or not copyable at all.
        copyable: :class:`bool`
            Indicates whether the level should be copyable.
        data: Union[:class:`bytes`, :class:`str`]
            The data of the level, as a stream.
        description: :class:`str`
            The description of the level.
        load: :class:`bool`
            Indicates whether the newly uploaded level should be loaded and returned.
            If false, the ``gd.Level(id=id, client=self)`` is returned.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to upload a level.

        Returns
        -------
        :class:`.Level`
            Newly uploaded level.
        """
        if objects is None:
            objects = len(utils.object_split(data))

        length = LevelLength.from_value(length)

        level_id = await self.session.upload_level(
            data=data,
            name=name,
            level_id=id,
            version=version,
            length=length,
            audio_track=track,
            song_id=song_id,
            is_auto=is_auto,
            original=original,
            two_player=two_player,
            objects=objects,
            coins=coins,
            stars=star_amount,
            unlisted=unlist,
            ldm=ldm,
            password=password,
            copyable=copyable,
            desc=description,
            client=self,
        )

        if load:
            return await self.get_level(level_id)
        else:
            return Level(id=level_id, client=self)

    @check_logged
    async def get_page_levels(
        self, page: int = 0, *, exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE
    ) -> List[Level]:
        """|coro|

        Gets levels of a client from a server.

        .. note::

            This method requires client to be logged in.

        Parameters
        ----------
        page: :class:`int`
            Page to look levels at.

        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.Level`]
            All levels found, as list. Might be an empty list.

        Raises
        ------
        :exc:`.MissingAccess`
            No levels were found.
        """
        filters = Filters.setup_by_user()
        return await self.search_levels_on_page(filters=filters, exclude=exclude)

    @check_logged
    async def get_levels(self, pages: Optional[Iterable[int]] = range(10)) -> List[Level]:
        """|coro|

        Searches for levels on given pages.

        .. note::

            This method requires authorised client.

        Parameters
        ----------
        pages: Iterable[:class:`int`]
            Pages to look for levels at.

        Returns
        -------
        List[:class:`.Level`]
            All levels found, as list, which might be empty.
        """
        filters = Filters.setup_by_user()
        return await self.search_levels(pages=pages, filters=filters)

    @check_logged
    async def load(self) -> None:
        """|coro|

        Loads save from a server and parses it.
        Sets :attr:`.Client.save` to :class:`.Save` namedtuple ``(completed, followed)``.
        """
        db, save = await self.session.load_save(client=self)

        if db is None or save is None:  # pragma: no cover
            log.warning("Failed to load a save.")
        else:
            self.edit(db=db, save=save)
            log.info("Successfully loaded a save.")

    @check_logged
    async def backup(self, save_data: Optional[Sequence[Union[bytes, str]]] = None) -> None:
        """|coro|

        Back up the data of the client.

        Parameters
        ----------
        save_data: Union[:class:`bytes`, :class:`str`]
            Save data to backup.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to do a backup.
        """
        if save_data is None and self.db is None:
            return log.warning("No data was provided.")

        if not save_data:
            data = await api.save.to_string_async(self.db, connect=False, xor=False)
        else:
            data = save_data

        await self.session.do_save(client=self, data=data)

    def close(self, message: Optional[str] = None) -> None:
        """*Closes* client.

        Basically sets its password and username to ``None``, which
        actually implies that client logs out.

        Parameters
        ----------
        message: :class:`str`
            A message to print after closing.
        """
        self._set_to_defaults()

        log.info("Has logged out with message: %r", message)

    def temp_login(self, user: str, password: str) -> Any:
        """Async context manager, used for temporarily logging in.

        Typical usage can be, as follows:

        .. code-block:: python3

            async with client.temp_login('Name', 'Password'):
                await client.post_comment('Hey there from gd.py!')
        """
        return LoginSession(self, user, password)

    @check_logged
    async def like(self, entity: Union[Comment, Level]) -> None:
        """|coro|

        Like an entity (either a comment or a level).

        Parameters
        ----------
        entity: Union[:class:`.Comment`, :class:`.Level`]
            An entity to like.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to like an entity.
        """
        typeid, special = figure_type_and_special(entity)
        await self.session.like(entity.id, typeid, special, dislike=False, client=self)

    @check_logged
    async def dislike(self, entity: Union[Comment, Level]) -> None:
        """|coro|

        Dislike an entity (either a comment or a level).

        Parameters
        ----------
        entity: Union[:class:`.Comment`, :class:`.Level`]
            An entity to like.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to dislike an entity.
        """
        typeid, special = figure_type_and_special(entity)
        await self.session.like(entity.id, typeid, special, dislike=True, client=self)

    @check_logged
    async def delete_comment(self, comment: Comment) -> None:
        """|coro|

        Delete a comment.

        Parameters
        ----------
        comment: :class:`.Comment`
            A comment to delete.

        Raises
        ------
        :exc:`.MissingAccess`
            Server did not return 1, which means comment was not deleted.
        """
        await self.session.delete_comment(comment.type, comment.id, comment.level_id, client=self)

    @check_logged
    async def read_friend_request(self, request: FriendRequest) -> None:
        """|coro|

        Read a friend request.

        Parameters
        ----------
        request: :class:`.FriendRequest`
            A friend request to read.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to read a request.
        """
        await self.session.read_friend_request(request.id, client=self)
        request.options.update(is_read=True)

    @check_logged
    async def delete_friend_request(self, request: FriendRequest) -> None:
        """|coro|

        Delete a friend request.

        Parameters
        ----------
        request: :class:`.FriendRequest`
            A friend request to delete.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a friend request.
        """
        await self.session.delete_friend_request(
            request.type, request.author.account_id, client=self
        )

    @check_logged
    async def accept_friend_request(self, request: FriendRequest) -> None:
        """|coro|

        Accept a friend request.

        Parameters
        ----------
        request: :class:`.FriendRequest`
            A friend request to accept.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to accept a friend request.
        """
        await self.session.accept_friend_request(
            request.type, request.id, request.author.account_id, client=self
        )

    @check_logged
    async def read_message(self, message: Message) -> str:
        """|coro|

        Read a message.

        Parameters
        ----------
        message: :class:`.Message`
            A message to read.

        Returns
        -------
        :class:`str`
            The content of the message.
        """
        body = await self.session.read_message(message.type, message.id, client=self)
        message.body = body
        message.options.update(is_read=True)
        return body

    @check_logged
    async def delete_message(self, message: Message) -> None:
        """|coro|

        Delete a message.

        Parameters
        ----------
        message: :class:`.Message`
            A message to delete.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a message.
        """
        await self.session.delete_message(message.type, message.id, client=self)

    @check_logged
    async def send_message(self, user: AbstractUser, subject: str, body: str) -> Optional[Message]:
        """|coro|

        Send a message.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to send a message to.
        subject: :class:`str`
            Subject of a new message.
        body: :class:`str`
            Body of a new message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a message.

        Returns
        -------
        Optional[:class:`.Message`]
            Sent message.
        """
        await self.session.send_message(user.account_id, subject=subject, body=body, client=self)

        if self.load_after_post:
            messages = await self.get_page_messages("sent")
            message = utils.get(messages, subject=subject, recipient=user)

            if message is None:
                return

            message.body = body
            return message

    @check_logged
    async def block(self, user: AbstractUser) -> None:
        """|coro|

        Block a user.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to block.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to block a user.
        """
        await self.session.block_user(user.account_id, unblock=False, client=self)

    @check_logged
    async def unblock(self, user: AbstractUser) -> None:
        """|coro|

        Unblock a user.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to unblock.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to unblock a user.
        """
        await self.session.block_user(user.account_id, unblock=True, client=self)

    @check_logged
    async def unfriend(self, user: AbstractUser) -> None:
        """|coro|

        Unfriend a user.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to unfriend.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to unfriend a user.
        """
        await self.session.unfriend_user(user.account_id, client=self)

    @check_logged
    async def send_friend_request(
        self, user: AbstractUser, message: str = ""
    ) -> Optional[FriendRequest]:
        """|coro|

        Send a friend request.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to send a request to.

        message: :class:`str`
            Body of friend request message.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a friend request to user.

        Returns
        -------
        Optional[:class:`.FriendRequest`]
            Sent friend request.
        """
        await self.session.send_friend_request(user.account_id, message=message, client=self)

        if self.load_after_post:
            requests = await self.get_page_friend_requests("sent")
            return utils.get(requests, recipient=user)

    async def retrieve_page_comments(
        self,
        user: AbstractUser,
        type: str = "profile",
        page: int = 0,
        strategy: Union[int, str, CommentStrategy] = 0,
        exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE,
    ) -> List[Comment]:
        """|coro|

        Retrieve comments of a user.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to retrieve comments of.
        type: :class:`str`
            Type of comments to look for.
            Either ``profile`` or ``level``.
        page: :class:`int`
            Page to look comments on.
        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.
        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            Strategy to use. ``recent`` or ``most_liked``.

        Returns
        -------
        List[:class:`.Comment`]
            Retrieved comments.
        """
        strategy = CommentStrategy.from_value(strategy)
        data = await self.session.retrieve_page_comments(
            user.account_id, user.id, type=type, page=page, exclude=exclude, strategy=strategy,
        )
        return list(Comment.from_data(part, user, client=self) for part in data)

    async def retrieve_comments(
        self,
        user: AbstractUser,
        type: str = "profile",
        pages: Optional[Iterable[int]] = range(10),
        strategy: Union[int, str, CommentStrategy] = 0,
    ) -> List[Comment]:
        """|coro|

        Retrieve comments of a user.

        Parameters
        ----------
        user: :class:`.AbstractUser`
            User to retrieve comments of.
        type: :class:`str`
            Type of comments to look for.
            Either ``profile`` or ``level``.
        pages: Iterable[:class:`int`]
            Pages to look comments on.
        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            Strategy to use. ``recent`` or ``most_liked``.

        Returns
        -------
        List[:class:`.Comment`]
            Retrieved comments.
        """
        strategy = CommentStrategy.from_value(strategy)
        data = await self.session.retrieve_comments(
            user.account_id, user.id, type=type, pages=pages, strategy=strategy
        )
        return list(Comment.from_data(part, user, client=self) for part in data)

    async def report_level(self, level: Level) -> None:
        """|coro|

        Report a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to report.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to report a level.
        """
        await self.session.report_level(level.id)

    @check_logged
    async def delete_level(self, level: Level) -> None:
        """|coro|

        Delete a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to delete.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to delete a level.
        """
        await self.session.delete_level(level.id, client=self)
        level.is_alive = is_alive_mock

    @check_logged
    async def update_level_description(self, level: Level, content: str) -> None:
        """|coro|

        Update description a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to update description of.

        content: :class:`str`
            Content of a new description.
        """
        await self.session.update_level_desc(level.id, content, client=self)
        level.options.update(description=content)

    @check_logged
    async def rate_level(self, level: Level, stars: int = 1) -> None:
        """|coro|

        Rate a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to rate.

        stars: :class:`int`
            Amount of stars to rate a level with.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to rate a level.
        """
        await self.session.rate_level(level.id, stars, client=self)

    @check_logged
    async def rate_demon(
        self,
        level: Level,
        demon_difficulty: Union[int, str, DemonDifficulty] = 1,
        as_mod: bool = False,
    ) -> None:
        """|coro|

        Rate a level as demon.

        Parameters
        ----------
        level: :class:`.Level`
            A level to rate.
        demon_difficulty: Union[:class:`int`, :class:`str`, :class:`.DemonDifficulty`]
            Demon difficulty to rate a level with.
        as_mod: :class:`bool`
            Whether to attempt to rate a level as moderator.
        """
        demon_difficulty = DemonDifficulty.from_value(demon_difficulty)

        success = await self.session.rate_demon(level.id, demon_difficulty, mod=as_mod, client=self)

        if success:
            log.info("Successfully demon-rated level: %s.", level)
        else:
            log.warning("Failed to rate demon difficulty for level: %s.", level)

    @check_logged
    async def send_level(self, level: Level, stars: int = 1, featured: bool = True) -> None:
        """|coro|

        Send a level to RobTop.

        Parameters
        ----------
        level: :class:`.Level`
            A level to send.

        stars: :class:`int`
            Amount of stars to send a level with.

        featured: :class:`bool`
            Whether to send a level for feature.

        Raises
        ------
        :exc:`.MissingAccess`
            Missing required moderator permissions.
        """
        await self.session.send_level(level.id, stars, featured=featured, client=self)

    @check_logged
    async def comment_level(
        self, level: Level, content: str, percentage: int = 0
    ) -> Optional[Comment]:
        """|coro|

        Comment a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to comment.

        content: :class:`str`
            Content of a comment to post.

        precentage: :class:`int`
            Percentage to put a comment with.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to post a level comment.

        Returns
        -------
        Optional[:class:`.Comment`]
            Sent comment.
        """
        await self.session.comment_level(level.id, content, percentage, client=self)

        if self.load_after_post:
            comments = await level.get_comments()
            return utils.get(comments, author=self.as_user(), body=content)

    @check_logged
    async def get_level_leaderboard(
        self, level: Level, strategy: Union[int, str, LevelLeaderboardStrategy]
    ) -> List[LevelRecord]:
        """|coro|

        Get leaderboard of a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to fetch a leaderboard of.

        strategy: Union[:class:`int`, :class:`str`, :class:`.LevelLeaderboardStrategy`]
            Strategy to use when fetching a leaderboard.

        Returns
        -------
        List[:class:`.LevelRecord`]
            Level records that were found.
        """
        strategy = LevelLeaderboardStrategy.from_value(strategy)
        data = await self.session.get_leaderboard(level.id, strategy=strategy, client=self)
        return list(LevelRecord.from_data(part, strategy=strategy, client=self) for part in data)

    async def get_level_comments(
        self,
        level: Level,
        strategy: Union[int, str, CommentStrategy] = 0,
        amount: int = 20,
        exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE,
    ) -> List[Comment]:
        """|coro|

        Get comments of a level.

        Parameters
        ----------
        level: :class:`.Level`
            A level to fetch comments of.

        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            Strategy to use when fetching a leaderboard.

        amount: :class:`int`
            Amount of comments to fetch. When lower than *0*, adds *2^31* to the amount.
            (meaning to fetch all the comments)

        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.Comment`]
            Comments that were found.
        """
        if amount < 0:
            amount += 2 ** 31  # 2,147,483,648 is enough?! ~ nekit

        data = await self.session.get_level_comments(
            level_id=level.id,
            strategy=CommentStrategy.from_value(strategy),
            amount=amount,
            exclude=exclude,
        )
        return list(Comment.from_data(part, user_data, client=self) for (part, user_data) in data)

    @check_logged
    async def get_blocked_users(
        self, exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE
    ) -> List[AbstractUser]:
        """|coro|

        Get all users blocked by a client.

        Parameters
        ----------
        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.AbstractUser`]
            All blocked users retrieved, as list.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to fetch blocked users of a client.

        :exc:`.NothingFound`
            No blocked users were found. Cool.
        """
        data = await self.session.get_user_list(type=1, exclude=exclude, client=self)
        return list(AbstractUser.from_data(part, client=self) for part in data)

    @check_logged
    async def get_friends(
        self, exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE
    ) -> List[AbstractUser]:
        """|coro|

        Get all friends of a client.

        Parameters
        ----------
        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.AbstractUser`]
            All friends retrieved, as list.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to fetch friends of a client.

        :exc:`.NothingFound`
            No friends were found. Sadly...
        """
        data = await self.session.get_user_list(type=0, exclude=exclude, client=self)
        return list(AbstractUser.from_data(part, client=self) for part in data)

    @check_logged
    async def to_user(self) -> User:
        """|coro|

        Gets user with :attr:`.Client.account_id`,
        which means that client should be logged in.

        Returns
        -------
        :class:`.User`
            User corresponding to :attr:`.Client.account_id`.
        """
        return await self.get_user(self.account_id)

    @check_logged
    async def get_page_messages(
        self,
        sent_or_inbox: str = "inbox",
        page: int = 0,
        *,
        exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE,
    ) -> List[Message]:
        """|coro|

        Gets messages on a specified page.

        Requires logged in client.

        Parameters
        ----------
        sent_or_inbox: :class:`str`
            The type of messages to look for. Either *inbox* or *sent*.

        page: :class:`int`
            Number of page to look at.

        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.Message`]
            List of messages found. Can be empty.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to get messages.

        :exc:`.NothingFound`
            No messages were found.
        """
        data = await self.session.get_page_messages(
            sent_or_inbox=sent_or_inbox, page=page, exclude=exclude, client=self
        )
        return list(Message.from_data(part, self.get_parse_dict(), client=self) for part in data)

    @check_logged
    async def get_messages(
        self, sent_or_inbox: str = "inbox", pages: Optional[Iterable[int]] = range(10)
    ) -> List[Message]:
        """|coro|

        Retrieves messages from given ``pages``.

        Parameters
        ----------
        sent_or_inbox: :class:`str`
            Type of messages to retrieve. Either `'sent'` or `'inbox'`.
            Defaults to the latter.

        pages: Iterable[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.Message`]
            List of messages found. Can be an empty list.
        """
        data = await self.session.get_messages(
            sent_or_inbox=sent_or_inbox, pages=pages, client=self
        )

        return list(Message.from_data(part, self.get_parse_dict(), client=self) for part in data)

    @check_logged
    async def get_page_friend_requests(
        self,
        sent_or_inbox: str = "inbox",
        page: int = 0,
        *,
        exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE,
    ) -> List[FriendRequest]:
        """|coro|

        Gets friend requests on a specified page.

        Requires logged in client.

        Parameters
        ----------
        sent_or_inbox: :class:`str`
            The type of friend requests to look for. Either *inbox* or *sent*.

        page: :class:`int`
            Number of page to look at.

        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.FriendRequest`]
            List of friend requests found. Can be empty.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to get friend requests.

        :exc:`.NothingFound`
            No friend requests were found.
        """
        data = await self.session.get_page_friend_requests(
            sent_or_inbox=sent_or_inbox, page=page, exclude=exclude, client=self
        )
        return list(
            FriendRequest.from_data(part, self.get_parse_dict(), client=self) for part in data
        )

    @check_logged
    async def get_friend_requests(
        self, sent_or_inbox: str = "inbox", pages: Optional[Iterable[int]] = range(10)
    ) -> List[FriendRequest]:
        """|coro|

        Retrieves friend requests from given ``pages``.

        Parameters
        ----------
        sent_or_inbox: :class:`str`
            Type of friend requests to retrieve. Either `'sent'` or `'inbox'`.
            Defaults to the latter.

        pages: Iterable[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.FriendRequests`]
            List of friend requests found. Can be an empty list.
        """
        data = await self.session.get_friend_requests(
            sent_or_inbox=sent_or_inbox, pages=pages, client=self
        )
        return list(
            FriendRequest.from_data(part, self.get_parse_dict(), client=self) for part in data
        )

    @check_logged
    def get_parse_dict(self) -> ExtDict:
        return ExtDict({k: getattr(self, k) for k in ("name", "id", "account_id")})

    @check_logged
    def as_user(self) -> AbstractUser:
        return AbstractUser(**self.get_parse_dict(), client=self)

    async def get_top(
        self, strategy: Union[int, str, LeaderboardStrategy] = 0, *, count: int = 100
    ) -> List[UserStats]:
        """|coro|

        Fetches user top by given strategy.

        Example:

        .. code-block:: python3

            # getting top 10 creators
            top10_creators = await client.get_top('creators', count=10)

        .. note::

            Players Top 100 has stopped refreshing in 2.1 version of Geometry Dash.
            However, you can fetch it by searching using ``'relative'`` strategy
            and giving huge ``count`` argument.

            Also, please note that searching with ``'friends'`` and ``'relative'`` strategies
            requires logged in client.

        Parameters
        ----------
        strategy: Union[:class:`int`, :class:`str`, :class:`.LeaderboardStrategy`]
            Strategy to apply when searching.

        Returns
        -------
        List[:class:`.UserStats`]
        """
        strategy = LeaderboardStrategy.from_value(strategy)
        data = await self.session.get_top(strategy=strategy, count=count, client=self)
        return list(UserStats.from_data(part, client=self) for part in data)

    async def get_leaderboard(
        self, strategy: Union[int, str, LeaderboardStrategy] = 0, *, count: int = 100
    ) -> List[UserStats]:
        """|coro|

        This is an alias for :meth:`.Client.get_top`.
        """
        return await self.get_top(strategy, count=count)

    @check_logged
    async def post_comment(self, content: str) -> Optional[Comment]:
        """|coro|

        Post a profile comment.

        Parameters
        ----------
        content: :class:`str`
            The content of a comment.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to post a comment.

        Returns
        -------
        Optional[:class:`.Comment`]
            Posted comment.
        """
        await self.session.post_comment(content, client=self)

        log.debug("Posted a comment. Content: %r", content)

        if self.load_after_post:
            user = self.as_user()
            comments = await user.get_page_comments()
            return utils.get(comments, author=user, body=content)

    @check_logged
    async def update_profile(
        self,
        stars: Optional[int] = None,
        demons: Optional[int] = None,
        diamonds: Optional[int] = None,
        has_glow: Optional[bool] = None,
        icon_type: Optional[Union[int, str, IconType]] = None,
        icon: Optional[int] = None,
        color_1: Optional[int] = None,
        color_2: Optional[int] = None,
        coins: Optional[int] = None,
        user_coins: Optional[int] = None,
        cube: Optional[int] = None,
        ship: Optional[int] = None,
        ball: Optional[int] = None,
        ufo: Optional[int] = None,
        wave: Optional[int] = None,
        robot: Optional[int] = None,
        spider: Optional[int] = None,
        explosion: Optional[int] = None,
        special: int = 0,
        set_as_user: Optional[User] = None,
    ) -> None:
        """|coro|

        Updates the profile of a client.

        .. note::

            gd.py developers are not responsible for any effects that calling this function
            may cause. Use this method on your own risk.

        Parameters
        ----------
        stars: :class:`int`
            An amount of stars to set.
        demons: :class:`int`
            An amount of completed demons to set.
        diamonds: :class:`int`
            An amount of diamonds to set.
        has_glow: :class:`bool`
            Indicates whether a user should have the glow outline.
        icon_type: :class:`int`
            Icon type that should be used. See :class:`.IconType` for info.
        icon: :class:`int`
            Icon ID that should be used.
        color_1: :class:`int`
            Index of a color to use as the main color.
        color_2: :class:`int`
            Index of a color to use as the secodary color.
        coins: :class:`int`
            An amount of secret coins to set.
        user_coins: :class:`int`
            An amount of user coins to set.
        cube: :class:`int`
            An index of a cube icon to apply.
        ship: :class:`int`
            An index of a ship icon to apply.
        ball: :class:`int`
            An index of a ball icon to apply.
        ufo: :class:`int`
            An index of a ufo icon to apply.
        wave: :class:`int`
            An index of a wave icon to apply.
        robot: :class:`int`
            An index of a robot icon to apply.
        spider: :class:`int`
            An index of a spider icon to apply.
        explosion: :class:`int`
            An index of a explosion to apply.
        special: :class:`int`
            The purpose of this parameter is unknown.
        set_as_user: :class:`.User`
            Passing this parameter allows to copy user's profile.
        """
        if set_as_user is None:
            set_as_user = await self.to_user()

        user, iconset = set_as_user, set_as_user.icon_set

        stats_dict = {
            "stars": value_or(stars, user.stars),
            "demons": value_or(demons, user.demons),
            "diamonds": value_or(diamonds, user.diamonds),
            "color1": value_or(color_1, iconset.color_1.index),
            "color2": value_or(color_2, iconset.color_2.index),
            "coins": value_or(coins, user.coins),
            "user_coins": value_or(user_coins, user.user_coins),
            "special": special,
            "icon": value_or(icon, iconset.main),
            "icon_type": IconType.from_value(value_or(icon_type, iconset.main_type)).value,
            "acc_icon": value_or(cube, iconset.cube),
            "acc_ship": value_or(ship, iconset.ship),
            "acc_ball": value_or(ball, iconset.ball),
            "acc_bird": value_or(ufo, iconset.ufo),
            "acc_dart": value_or(wave, iconset.wave),
            "acc_robot": value_or(robot, iconset.robot),
            "acc_spider": value_or(spider, iconset.spider),
            "acc_explosion": value_or(explosion, iconset.explosion),
            "acc_glow": int(value_or(has_glow, iconset.has_glow_outline())),
        }

        await self.session.update_profile(stats_dict, client=self)

    @check_logged
    async def update_settings(
        self,
        *,
        message_policy: Optional[Union[int, str, MessagePolicyType]] = None,
        friend_request_policy: Optional[Union[int, str, FriendRequestPolicyType]] = None,
        comment_policy: Optional[Union[int, str, CommentPolicyType]] = None,
        youtube: Optional[str] = None,
        twitter: Optional[str] = None,
        twitch: Optional[str] = None,
    ) -> None:
        """|coro|

        Updates profile settings of a client.

        .. note::

            For parameter in parameters, if parameter is ``None`` or omitted,
            it will be set to the current policy/link of the user corresponding
            to this client; that implies that running the following:

            .. code-block:: python3

                await client.update_settings()

            will cause no effect on profile settings.

        Parameters
        ----------
        message_policy: Union[:class:`int`, :class:`str`, :class:`.MessagePolicyType`]
            New message policy.
        friend_request_policy: Union[:class:`int`, :class:`str`, :class:`.FriendRequestPolicyType`]
            New friend request policy.
        comment_policy: Union[:class:`int`, :class:`str`, :class:`.CommentPolicyType`]
            New comment history policy.
        youtube: :class:`str`
            New youtube channel string. (not link)
        twitter: :class:`str`
            New twitter profile name.
        twitch: :class:`str`
            New twitch profile name.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to update profile.
        """
        user = await self.to_user()

        profile_dict = {
            "message_policy": MessagePolicyType.from_value(
                value_or(message_policy, user.message_policy)
            ),
            "friend_request_policy": FriendRequestPolicyType.from_value(
                value_or(friend_request_policy, user.friend_request_policy)
            ),
            "comment_policy": CommentPolicyType.from_value(
                value_or(comment_policy, user.comment_policy)
            ),
            "youtube": value_or(youtube, user.youtube),
            "twitter": value_or(twitter, user.twitter),
            "twitch": value_or(twitch, user.twitch),
        }

        await self.session.update_settings(**profile_dict, client=self)

    @check_logged
    async def get_quests(self) -> List[Quest]:
        data = await self.session.get_quests(client=self)
        return list(Quest(**part, client=self) for part in data)

    @check_logged
    async def get_chests(self, reward_type: Union[int, str, RewardType] = 0) -> List[Chest]:
        reward_type = RewardType.from_value(reward_type)

        data = await self.session.get_chests(reward_type, client=self)

        return list(Chest(**part, client=self) for part in data)

    async def search_levels_on_page(
        self,
        page: int = 0,
        query: Union[str, int] = "",
        filters: Optional[Filters] = None,
        user: Optional[Union[int, AbstractUser]] = None,
        gauntlet: Optional[Union[Gauntlet, int]] = None,
        *,
        exclude: Tuple[Type[BaseException]] = DEFAULT_EXCLUDE,
    ) -> List[Level]:
        """|coro|

        Searches levels on given page by given query, applying filters as well.

        Parameters
        ----------
        page: :class:`int`
            A page to search levels on.

        query: Union[:class:`str`, :class:`int`]
            A query to search with.

        filters: :class:`.Filters`
            Filters to apply, as an object.

        user: Union[:class:`int`, :class:`.AbstractUser`]
            A user to search levels by. (if :class:`.Filters` has parameter ``strategy``
            equal to :class:`.SearchStrategy` ``BY_USER``. Can be omitted, then
            logged in client is required.)

        gauntlet: Union[:class:`int`, :class:`.Gauntlet`]
            A gauntlet to get levels in.

        exclude: Sequence[Type[:exc:`BaseException`]]
            Exceptions to ignore. By default includes only :exc:`.NothingFound`.

        Returns
        -------
        List[:class:`.Level`]
            Levels found on given page.
        """
        if isinstance(user, AbstractUser):
            user = user.id

        if isinstance(gauntlet, Gauntlet):
            gauntlet = gauntlet.id

        lvdata, cdata, sdata = await self.session.search_levels_on_page(
            page=page,
            query=query,
            filters=filters,
            user_id=user,
            gauntlet=gauntlet,
            exclude=exclude,
            client=self,
        )

        return construct_levels(lvdata, cdata, sdata, client=self)

    async def search_levels(
        self,
        query: Union[str, int] = "",
        filters: Optional[Filters] = None,
        user: Optional[Union[int, AbstractUser]] = None,
        gauntlet: Optional[Union[int, Gauntlet]] = None,
        pages: Optional[Iterable[int]] = range(10),
    ) -> List[Level]:
        """|coro|

        Searches levels on given pages.

        Parameters
        ----------
        query: Union[:class:`str`,:class:`int`]
            A query to search with.

        filters: :class:`.Filters`
            Filters to apply, as an object.

        user: Union[:class:`int`, :class:`.AbstractUser`]
            A user to search levels by. (if :class:`.Filters` has parameter ``strategy``
            equal to :class:`.SearchStrategy` ``BY_USER``. Can be omitted, then
            logged in client is required.)

        pages: Iterable[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.Level`]
            List of levels found. Can be an empty list.
        """
        if isinstance(user, AbstractUser):
            user = user.id

        if isinstance(gauntlet, Gauntlet):
            gauntlet = gauntlet.id

        lvdata, cdata, sdata = await self.session.search_levels(
            query=query, filters=filters, user_id=user, gauntlet=gauntlet, pages=pages, client=self
        )

        return utils.unique(construct_levels(lvdata, cdata, sdata, client=self))

    async def on_new_daily(self, level: Level) -> Any:
        """|coro|

        This is an event that is fired when a new daily level is set.

        See :ref:`events` for more info.
        """
        pass

    async def on_new_weekly(self, level: Level) -> Any:
        """|coro|

        This is an event that is fired when a new weekly demon is assigned.

        See :ref:`events` for more info.
        """
        pass

    async def on_level_rated(self, level: Level) -> Any:
        """|coro|

        This is an event that is fired when a new level is rated.

        See :ref:`events` for more info.
        """
        pass

    async def on_level_unrated(self, level: Level) -> Any:
        """|coro|

        This is an event that is fired when a level is unrated.

        See :ref:`events` for more info.
        """
        pass

    async def on_message(self, message: Message) -> Any:
        """|coro|

        This is an event that is fired when a logged in client gets a message.

        See :ref:`events` for more info.
        """
        pass

    async def on_friend_request(self, friend_request: FriendRequest) -> Any:
        """|coro|

        This is an event that is fired when a logged in client gets a friend request.

        See :ref:`events` for more info.
        """
        pass

    async def on_level_comment(self, level: Level, comment: Comment) -> Any:
        """|coro|

        This is an event that is fired when a comment is posted on some level.

        See :ref:`events` for more info.
        """
        pass

    def listen_for(self, type: str, entity_id: Optional[int] = None, delay: Optional[float] = None) -> None:
        lower = str(type).lower()

        kwargs = {"client": self}

        if delay is not None:
            kwargs["delay"] = delay

        if lower in {"daily", "weekly"}:
            listener = TimelyLevelListener(t_type=lower, **kwargs)

        elif lower in {"rate", "unrate"}:
            listener = RateLevelListener(listen_to_rate=(lower == "rate"), **kwargs)

        elif lower in {"friend_request", "message"}:
            listener = MessageOrRequestListener(listen_to_msg=(lower == "message"), **kwargs)

        elif lower in {"level_comment"}:
            if entity_id is None:
                raise ClientException(f"Entity ID is required for type: {lower!r}.")

            listener = LevelCommentListener(level_id=entity_id, **kwargs)

        else:
            raise ClientException(f"Invalid listener type: {type!r}.")

        self.listeners.append(listener)

        return self.event  # allow using as a decorator

    async def dispatch(self, event_name: str, *args, **kwargs) -> Any:
        name = "on_" + event_name

        log.info(f"Dispatching event {name!r}, client: {self!r}")

        try:
            method = getattr(self, name)

        except AttributeError:
            return

        return await utils.maybe_coroutine(method, *args, **kwargs)

    def run(self, coro: Coroutine, *, debug: bool = False) -> Any:
        """A handy shortcut for :func:`.utils.run`.

        This is equivalent to:

        .. code-block:: python3

            gd.utils.run(coro, loop=self.loop, debug=debug)
        """
        return utils.run(coro, loop=self.loop, debug=debug)

    def event(self, coro: Coroutine) -> Coroutine:
        """A decorator that registers an event to listen to.

        Events must be a |coroutine_link|_, if not, :exc:`TypeError` is raised.

        Example
        -------

        .. code-block:: python3

            @client.event
            async def on_level_rated(level):
                print(level.name)

        Raises
        ------
        TypeError
            The coroutine passed is not actually a coroutine.
        """

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function.")

        setattr(self, coro.__name__, coro)
        log.debug("%s has been successfully registered as an event.", coro.__name__)

        return coro


class LoginSession:
    """Small wrapper around Client.login method.
    Allows to temporarily login and execute
    a block of code in an <async with> statement.
    """

    def __init__(self, client: Client, username: str, password: str) -> None:
        self._client = client
        self._name = username
        self._pass = password

    async def __aenter__(self) -> Client:
        await self._client.login(self._name, self._pass)
        return self._client

    async def __aexit__(self, *exc) -> None:
        self._client.close()


def value_or(value: Any, default: Any) -> Any:
    return default if value is None else value
