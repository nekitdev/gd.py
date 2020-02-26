import asyncio

from .errors import ClientException

from .logging import get_logger
from .typing import (
    AbstractUser, Any, ArtistInfo, Client, Comment, Coroutine, Dict,
    FriendRequest, Gauntlet, IconSet, Iterable, Level, LevelRecord, List,
    MapPack, Message, Optional, Sequence, Song, Union, User, UserStats
)
from .session import GDSession

from .events.listener import (
    TimelyLevelListener,
    RateLevelListener,
    MessageOrRequestListener,
    LevelCommentListener
)

from .utils.decorators import check_logged
from .utils.enums import (
    CommentPolicyType,
    CommentStrategy,
    DemonDifficulty,
    FriendRequestPolicyType,
    IconType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    MessagePolicyType,
)
from .utils.filters import Filters
from .utils.http_request import HTTPClient
from .utils.save_parser import Save
from .utils.text_tools import make_repr

from .utils.crypto.coders import Coder

from . import api
from . import utils

log = get_logger(__name__)


class Client:
    r"""A main class in the gd.py library, used for interacting with the servers of Geometry Dash.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used
        via :func:`.utils.acquire_loop`.

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
    database: Optional[:class:`.api.Database`]
        Save API. If not loaded, has empty parts inside.
    save: :class:`.Save`
        This is a namedtuple with format ``(completed, followed)``.
        Contains empty lists if not loaded.
    """
    def __init__(
        self, *, loop: Optional[asyncio.AbstractEventLoop] = None, **http_args
    ) -> None:
        self.session = GDSession(**http_args)
        self.loop = loop or utils.acquire_loop()
        self.listeners = list()
        self._set_to_defaults()

    def __repr__(self) -> str:
        info = {
            'is_logged': self.is_logged(),
            'account_id': self.account_id,
            'id': self.id,
            'name': self.name,
            'password': '...'
        }
        return make_repr(self, info)

    def _json(self) -> Dict[str, Optional[Union[int, str]]]:  # pragma: no cover
        return dict(
            account_id=self.account_id,
            id=self.id,
            name=self.name,
            password=None  # for safety reasons
        )

    def _set_to_defaults(self) -> None:
        self.save = Save(completed=list(), followed=list())
        self.save_api = api.Database()
        self.account_id = 0
        self.id = 0
        self.name = None
        self.password = None
        self.encodedpass = None

    def _upd(self, attr: str, value: Any) -> None:  # pragma: no cover
        setattr(self, attr, value)
        # update encodedpass if password was updated
        if attr == 'password':
            self.encodedpass = Coder.encode(type='accountpass', string=self.password)

    def edit(self, **attrs) -> Client:
        for attr, value in attrs.items():
            self._upd(attr, value)
        return self

    @property
    def http(self) -> HTTPClient:
        return self.session.http

    def is_logged(self) -> bool:
        return (self.name is not None) and (self.password is not None)

    async def ping_server(self) -> float:
        """|coro|

        Pings ``boomlings.com/database`` and returns the time taken.

        Returns
        -------
        :class:`float`
            Server ping, in milliseconds.
        """
        return await self.session.ping_server('http://boomlings.com/database/')

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
        return await self.session.test_song(song_id)

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
        return await self.session.get_song(song_id)

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
        return await self.session.get_ng_song(song_id)

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
        return await self.session.get_user(account_id, return_only_stats=False, client=self)

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
        user_stats = await self.session.get_user(account_id, return_only_stats=True, client=self)
        # return UserStats if needed, and AbstractUser otherwise.
        return user_stats if stats else user_stats.as_user()

    async def search_user(self, query: Union[int, str]) -> Union[AbstractUser, User]:
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
        Union[:class:`.User`, :class:`.AbstractUser`]
            A User found when searching with the query.
        """
        return await self.session.search_user(query, return_abstract=False, client=self)

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
        return await self.session.search_user(query, return_abstract=True, client=self)

    async def get_daily(self) -> Level:
        """|coro|

        Gets current daily level.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing found or invalid response was recieved.
        Returns
        -------
        :class:`.Level`
            Current daily level.
        """
        return await self.session.get_timely('daily', client=self)

    async def get_weekly(self) -> Level:
        """|coro|

        Gets current weekly demon.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing found or invalid response was recieved.
        Returns
        -------
        :class:`.Level`
            Current weekly demon.
        """
        return await self.session.get_timely('weekly', client=self)

    async def get_level(self, level_id: int = 0, get_data: bool = True) -> Level:
        """|coro|

        Fetches a level from Geometry Dash servers.

        Parameters
        ----------
        level_id: :class:`int`
            An ID of the level to fetch.

            .. note::

                If the given ID is *n*, and ``0 > n >= -2`` is ``True``,
                this function will search for daily/weekly levels, however,
                it is not recommended to use since it can cause confusion.
                Use :meth:`.Client.get_daily` and :meth:`.Client.get_weekly` instead.
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
            return await self.session.get_level(level_id, client=self)
        else:
            return (await self.search_levels_on_page(query=level_id)).pop(0)

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
        query = ','.join(map(str, level_ids))

        return await self.search_levels_on_page(query=query, filters=filters)

    async def get_gauntlets(self) -> List[Gauntlet]:
        """|coro|

        Fetches *The Lost Gauntlets*.

        Returns
        -------
        List[:class:`.Gauntlet`]
            All gauntlets retrieved, as list.
        """
        return await self.session.get_gauntlets(client=self)

    async def get_page_map_packs(self, page: int = 0, *, raise_errors: bool = True) -> List[MapPack]:
        """|coro|

        Fetches map packs on given page.

        Parameters
        ----------
        page: :class:`int`
            Page to look for map packs on.

        raise_errors: :class:`bool`
            Indicates whether :exc:`.NothingFound` should be raised. ``True`` by default.

        Returns
        -------
        List[:class:`.MapPack`]
            List of map packs retrieved.

        Raises
        ------
        :exc:`.NothingFound`
            No map packs were found at the given page.
        """
        return await self.session.get_page_map_packs(page=page, client=self)

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

        return await self.session.get_map_packs(pages=pages, client=self)

    async def login(self, user: str, password: str) -> None:  # pragma: no cover
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
        await self.session.login(client=self, user=user, password=password)
        log.info("Logged in as %r, with password %r.", user, password)

    @check_logged
    async def upload_level(
        self, name: str = 'Unnamed', id: int = 0, version: int = 1, length: int = 0,
        track: int = 0, song_id: int = 0, is_auto: bool = False, original: int = 0,
        two_player: bool = False, objects: Optional[int] = None, coins: int = 0, star_amount: int = 0,
        unlist: bool = False, ldm: bool = False, password: Optional[Union[int, str]] = None, copyable: bool = False,
        data: Union[bytes, str] = '', description: str = '', *, load: bool = True
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
        length: :class:`int`
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

        return await self.session.upload_level(
            data=data, name=name, level_id=id, version=version, length=length,
            audio_track=track, song_id=song_id, is_auto=is_auto, original=original,
            two_player=two_player, objects=objects, coins=coins, stars=star_amount,
            unlisted=unlist, ldm=ldm, password=password, copyable=copyable,
            desc=description, load_after=load, client=self
        )

    @check_logged
    async def get_page_levels(self, page: int = 0, *, raise_errors: bool = True) -> List[Level]:
        """|coro|

        Gets levels of a client from a server.

        .. note::

            This method requires client to be logged in.

        Parameters
        ----------
        page: :class:`int`
            Page to look levels at.

        raise_errors: :class:`bool`
            Indicates whether :exc:`.MissingAccess` should be raised. ``True`` by default.

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
        return await self.search_levels_on_page(filters=filters, raise_errors=raise_errors)

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
        success = await self.session.load_save(client=self)

        if success:
            log.info('Successfully loaded a save.')
        else:  # pragma: no cover
            log.warning('Failed to load a save.')

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
        if save_data is None and self.save_api is None:
            return log.warning('No data was provided.')

        if not save_data:
            data = await api.save.to_string_async(self.save_api, connect=False, xor=False)
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

        log.info('Has logged out with message: %r', message)

    def temp_login(self, user: str, password: str) -> Any:
        """Async context manager, used for temporarily logging in.

        Typical usage can be, as follows:

        .. code-block:: python3

            async with client.temp_login('Name', 'Password'):
                await client.post_comment('Hey there from gd.py!')
        """
        return _LoginSession(self, user, password)

    @check_logged
    async def like(self, entity: Union[Comment, Level]) -> None:
        await self.session.like(entity, dislike=False, client=self)

    @check_logged
    async def dislike(self, entity: Union[Comment, Level]) -> None:
        await self.session.like(entity, dislike=True, client=self)

    @check_logged
    async def delete_comment(self, comment: Comment) -> None:
        await self.session.delete_comment(comment, client=self)

    @check_logged
    async def read_friend_request(self, request: FriendRequest) -> None:
        await self.session.read_friend_req(request, client=self)

    @check_logged
    async def delete_friend_request(self, request: FriendRequest) -> None:
        await self.session.delete_friend_req(request, client=self)

    @check_logged
    async def accept_friend_request(self, request: FriendRequest) -> None:
        await self.session.accept_friend_req(request, client=self)

    @check_logged
    async def read_message(self, message: Message) -> str:
        return await self.session.read_message(message, client=self)

    @check_logged
    async def delete_message(self, message: Message) -> None:
        await self.session.delete_message(message, client=self)

    async def generate_icon(self, type: Union[int, str, IconType], icon_set: IconSet) -> bytes:
        form = IconType.from_value(type).name.lower()
        return await self.session.generate_icon(
            form=form, id=getattr(icon_set, form), has_glow=icon_set.has_glow_outline(),
            color_1=icon_set.color_1.index, color_2=icon_set.color_2.index
        )

    def make_user(self, user: AbstractUser) -> AbstractUser:
        return self.session.to_user(user._dict_for_parse, client=self)

    @check_logged
    async def send_message(self, user: AbstractUser, subject: str, body: str) -> None:
        await self.session.send_message(target=user, subject=subject, body=body, client=self)

    @check_logged
    async def block(self, user: AbstractUser) -> None:
        await self.session.block_user(user, unblock=False, client=self)

    @check_logged
    async def unblock(self, user: AbstractUser) -> None:
        await self.session.block_user(user, unblock=True, client=self)

    @check_logged
    async def unfriend(self, user: AbstractUser) -> None:
        await self.session.unfriend_user(user, client=self)

    @check_logged
    async def send_friend_request(self, user: AbstractUser, message: str) -> None:
        await self.session.send_friend_request(target=user, message=message, client=self)

    async def retrieve_page_comments(
        self, user: AbstractUser, type: str = 'profile', page: int = 0, *,
        raise_errors: bool = True, strategy: Union[int, str, CommentStrategy] = 0
    ) -> List[Comment]:
        strategy = CommentStrategy.from_value(strategy)
        return await self.session.retrieve_page_comments(
            type=type, user=user, page=page, raise_errors=raise_errors, strategy=strategy, client=self
        )

    async def retrieve_comments(
        self, user: AbstractUser, type: str = 'profile', pages: Optional[Iterable[int]] = range(10),
        strategy: Union[int, str, CommentStrategy] = 0
    ) -> List[Comment]:

        strategy = CommentStrategy.from_value(strategy)
        return await self.session.retrieve_comments(
            type=type, user=user, pages=pages, strategy=strategy, client=self
        )

    async def report_level(self, level: Level) -> None:
        await self.session.report_level(level)

    @check_logged
    async def delete_level(self, level: Level) -> None:
        await self.session.delete_level(level, client=self)

    @check_logged
    async def update_level_description(self, level: Level, content: str) -> None:
        await self.session.update_level_desc(level, content, client=self)

    @check_logged
    async def rate_level(self, level: Level, stars: int = 1) -> None:
        await self.session.rate_level(level, stars, client=self)

    @check_logged
    async def rate_demon(
        self, level: Level, demon_difficulty: Union[int, str, DemonDifficulty] = 1,
        as_mod: bool = False
    ) -> None:
        demon_difficulty = DemonDifficulty.from_value(demon_difficulty)

        success = await self.session.rate_demon(level, demon_difficulty, mod=as_mod, client=self)

        if success:
            log.info('Successfully demon-rated level: %s.', level)
        else:
            log.warning('Failed to rate demon difficulty for level: %s.', level)

    @check_logged
    async def send_level(
        self, level: Level, stars: int = 1, featured: bool = True
    ) -> None:
        await self.session.send_level(level, stars, featured=featured, client=self)

    @check_logged
    async def comment_level(
        self, level: Level, content: str, percentage: int = 0
    ) -> None:
        await self.session.comment_level(level, content, percentage, client=self)

    @check_logged
    async def get_level_leaderboard(
        self, level: Level, strategy: Union[int, str, LevelLeaderboardStrategy]
    ) -> List[LevelRecord]:
        strategy = LevelLeaderboardStrategy.from_value(strategy)
        return await self.session.get_leaderboard(level, strategy=strategy, client=self)

    async def get_level_comments(
        self, level: Level, strategy: Union[int, str, CommentStrategy] = 0, amount: int = 20
    ) -> List[Comment]:
        if amount < 0:
            amount += 2 ** 31

        return await self.session.get_level_comments(
            level=level, strategy=CommentStrategy.from_value(strategy), amount=amount, client=self)

    @check_logged
    async def get_blocked_users(self) -> List[AbstractUser]:
        """|coro|

        Get all users blocked by a client.

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
        return await self.session.get_user_list(type=1, client=self)

    @check_logged
    async def get_friends(self) -> List[AbstractUser]:
        """|coro|

        Get all friends of a client.

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
        return await self.session.get_user_list(type=0, client=self)

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
        self, sent_or_inbox: str = 'inbox', page: int = 0, *, raise_errors: bool = True
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

        raise_errors: :class:`bool`
            Indicates whether errors should be raised.

        Returns
        -------
        List[:class:`.Message`]
            List of messages found. Can be empty.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to get messages. Raised if ``raise_errors`` is ``True``.

        :exc:`.NothingFound`
            No messages were found. Raised if ``raise_errors`` is ``True``.
        """
        return await self.session.get_page_messages(
            sent_or_inbox=sent_or_inbox, page=page,
            raise_errors=raise_errors, client=self
        )

    @check_logged
    async def get_messages(
        self, sent_or_inbox: str = 'inbox', pages: Optional[Iterable[int]] = range(10)
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

        return await self.session.get_messages(
            sent_or_inbox=sent_or_inbox, pages=pages, client=self
        )

    @check_logged
    async def get_page_friend_requests(
        self, sent_or_inbox: str = 'inbox', page: int = 0, *, raise_errors: bool = True
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

        raise_errors: :class:`bool`
            Indicates whether errors should be raised.

        Returns
        -------
        List[:class:`.FriendRequest`]
            List of friend requests found. Can be empty.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to get friend requests. Raised if ``raise_errors`` is ``True``.

        :exc:`.NothingFound`
            No friend requests were found. Raised if ``raise_errors`` is ``True``.
        """
        return await self.session.get_page_friend_requests(
            sent_or_inbox=sent_or_inbox, page=page,
            raise_errors=raise_errors, client=self
        )

    @check_logged
    async def get_friend_requests(
        self, sent_or_inbox: str = 'inbox', pages: Optional[Iterable[int]] = range(10)
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

        return await self.session.get_friend_requests(
            sent_or_inbox=sent_or_inbox, pages=pages, client=self
        )

    @check_logged
    def get_parse_dict(self) -> Dict[str, Union[int, str]]:
        return {k: getattr(self, k) for k in ('name', 'id', 'account_id')}

    @check_logged
    def as_user(self) -> AbstractUser:
        return self.session.to_user(self.get_parse_dict(), client=self)

    async def get_top(
        self, strategy: Union[int, str, LeaderboardStrategy] = 0,
        *, count: int = 100
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
        return await self.session.get_top(strategy=strategy, count=count, client=self)

    async def get_leaderboard(
        self, strategy: Union[int, str, LeaderboardStrategy] = 0, *, count: int = 100
    ) -> List[UserStats]:
        """|coro|

        This is an alias for :meth:`.Client.get_top`.
        """
        return await self.get_top(strategy, count=count)

    @check_logged
    async def post_comment(self, content: str) -> None:
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
        """
        await self.session.post_comment(content, client=self)

        log.debug("Posted a comment. Content: %s", content)

    @check_logged
    async def update_profile(
        self, stars: int = 0, demons: int = 0, diamonds: int = 0, has_glow: bool = False,
        icon_type: int = 0, color_1: int = 0, color_2: int = 3, coins: int = 0,
        user_coins: int = 0, cube: int = 1, ship: int = 1, ball: int = 1, ufo: int = 1,
        wave: int = 1, robot: int = 1, spider: int = 1, explosion: int = 1, special: int = 0,
        set_as_user: Optional[User] = None
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
            stats_dict = {
                'stars': stars, 'demons': demons, 'diamonds': diamonds,
                'color1': color_1, 'color2': color_2,
                'coins': coins, 'user_coins': user_coins, 'special': special,
                'acc_icon': cube, 'acc_ship': ship, 'acc_ball': ball,
                'acc_bird': ufo, 'acc_dart': wave, 'acc_robot': robot,
                'acc_spider': spider, 'acc_explosion': explosion, 'acc_glow': int(has_glow)
            }

            icon_type = IconType.from_value(icon_type).value
            icon = (cube, ship, ball, ufo, wave, robot, spider)[icon_type]

            stats_dict.update(icon_type=icon_type, icon=icon)

        else:
            user, iconset = set_as_user, set_as_user.icon_set
            stats_dict = {
                'stars': user.stars, 'demons': user.demons, 'diamonds': user.diamonds,
                'color1': iconset.color_1.index, 'color2': iconset.color_2.index,
                'coins': user.coins, 'user_coins': user.user_coins, 'special': special,
                'icon': iconset.main, 'icon_type': iconset.main_type.value,
                'acc_icon': iconset.cube, 'acc_ship': iconset.ship, 'acc_ball': iconset.ball,
                'acc_bird': iconset.ufo, 'acc_dart': iconset.wave, 'acc_robot': iconset.robot,
                'acc_spider': iconset.spider, 'acc_explosion': iconset.explosion,
                'acc_glow': int(iconset.has_glow_outline())
            }

        await self.session.update_profile(stats_dict, client=self)

    @check_logged
    async def update_settings(
        self, *, msg: Optional[Union[int, MessagePolicyType]] = None,
        friend_req: Optional[Union[int, FriendRequestPolicyType]] = None,
        comments: Optional[Union[int, CommentPolicyType]] = None,
        youtube: Optional[str] = None, twitter: Optional[str] = None, twitch: Optional[str] = None
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
        msg: Union[:class:`int`, :class:`.MessagePolicyType`]
            New message policy.
        friend_req: Union[:class:`int`, :class:`.FriendRequestPolicyType`]
            New friend request policy.
        comments: Union[:class:`int`, :class:`.CommentPolicyType`]
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
        profile_dict = {
            'msg_policy': msg,
            'friend_req_policy': friend_req,
            'comments_policy': comments,
            'youtube': youtube,
            'twitter': twitter,
            'twitch': twitch
        }

        self_user = await self.to_user()

        args = []

        for attr, value in profile_dict.items():
            tmp = getattr(self_user, attr) if value is None else value
            if tmp is None:
                s = ''
            else:
                try:
                    s = int(tmp)
                except Exception:
                    s = str(tmp)

            args.append(s)

        await self.session.update_settings(*args, client=self)

    async def search_levels_on_page(
        self, page: int = 0, query: Union[str, int] = '', filters: Optional[Filters] = None,
        user: Optional[Union[int, AbstractUser, User]] = None, *, raise_errors: bool = True
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

        user: Union[:class:`int`, :class:`.AbstractUser`, :class:`.User`]
            A user to search levels by. (if :class:`.Filters` has parameter ``strategy``
            equal to :class:`.SearchStrategy` ``BY_USER``. Can be omitted, then
            logged in client is required.)

        raise_errors: :class:`bool`
            Whether or not to raise errors.

        Returns
        -------
        List[:class:`.Level`]
            Levels found on given page.

        Raises
        ------
        ``~ soon``
        """
        return await self.session.search_levels_on_page(
            page=page, query=query, filters=filters, user=user, raise_errors=raise_errors, client=self
        )

    async def search_levels(
        self, query: Union[str, int] = '', filters: Optional[Filters] = None,
        user: Optional[Union[int, AbstractUser, User]] = None, pages: Optional[Iterable[int]] = range(10)
    ) -> List[Level]:
        print(pages)
        """|coro|

        Searches levels on given pages.

        Parameters
        ----------
        query: Union[:class:`str`,:class:`int`]
            A query to search with.

        filters: :class:`.Filters`
            Filters to apply, as an object.

        user: Union[:class:`int`, :class:`.AbstractUser`, :class:`.User`]
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

        return await self.session.search_levels(
            query=query, filters=filters, user=user, pages=pages, client=self
        )

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

    def listen_for(self, type: str, entity_id: Optional[int] = None) -> None:
        lower = str(type).lower()

        if lower in {'daily', 'weekly'}:
            listener = TimelyLevelListener(self, lower)

        elif lower in {'rate', 'unrate'}:
            listener = RateLevelListener(self, listen_to_rate=(lower == 'rate'))

        elif lower in {'friend_request', 'message'}:
            listener = MessageOrRequestListener(self, listen_to_msg=(lower == 'message'))

        elif lower in {'level_comment'}:
            if entity_id is None:
                raise ClientException('Entity ID is required for type: {!r}.'.format(lower))

            listener = LevelCommentListener(self, entity_id)

        else:
            raise ClientException('Invalid listener type: {!r}.'.format(lower))

        self.listeners.append(listener)
        listener.enable()

        return self.event  # allow using as a decorator

    async def dispatch(self, event_name: str, *args, **kwargs) -> Any:
        name = 'on_' + event_name

        log.info('Dispatching event {!r}, client: {!r}'.format(name, self))

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


class _LoginSession:
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
