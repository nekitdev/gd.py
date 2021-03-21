# DOCUMENT

import traceback
import types

from gd.api.database import Database
from gd.api.recording import RecordingEntry
from gd.async_iters import async_iter, awaitable_iterator
from gd.async_utils import get_not_running_loop, maybe_await, maybe_coroutine
from gd.comment import Comment
from gd.crypto import Key, encode_robtop_str
from gd.decorators import cache_by, synchronize, login_check, login_check_object
from gd.enums import (
    AccountURLType,
    CommentState,
    CommentStrategy,
    CommentType,
    DemonDifficulty,
    FriendRequestState,
    FriendRequestType,
    IconType,
    LeaderboardStrategy,
    LevelLeaderboardStrategy,
    LevelLength,
    LikeType,
    MessageState,
    MessageType,
    RewardType,
    SimpleRelationshipType,
)
from gd.errors import ClientException, MissingAccess, NothingFound
from gd.events.listener import (
    AbstractListener,
    LevelCommentListener,
    MessageOrRequestListener,
    RateLevelListener,
    TimelyLevelListener,
    UserCommentListener,
)
from gd.filters import Filters
from gd.friend_request import FriendRequest
from gd.http import URL, HTTPClient
from gd.level import Level
from gd.level_packs import Gauntlet, MapPack
from gd.logging import get_logger
from gd.message import Message
from gd.model import LevelSearchResponseModel  # type: ignore
from gd.rewards import Chest, Quest
from gd.session import Session
from gd.song import ArtistInfo, Author, Song
from gd.text_utils import make_repr
from gd.typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)
from gd.user import User

__all__ = ("DAILY", "WEEKLY", "Client")

T = TypeVar("T")
AnyIterable = Union[AsyncIterable[T], Iterable[T]]

log = get_logger(__name__)

MaybeAsyncFunction = Callable[..., Union[T, Awaitable[T]]]
MaybeAwaitable = Union[Awaitable[T], T]

DAILY = -1
WEEKLY = -2

COMMENT_PAGE_SIZE = 20

CONCURRENT = True
PAGES = range(10)


def value_or(value: Optional[T], default: T) -> T:
    return default if value is None else value


def pages_for_amount(amount: int, page_size: int) -> Iterable[int]:
    if amount < 0:
        raise ValueError("Expected non-negative integer.")

    page = amount / page_size

    if not page.is_integer():
        page += 1

    return range(int(page))


def run_async_iterators(
    iterators: AnyIterable[AnyIterable[T]],
    *ignore_exceptions: Type[BaseException],
    concurrent: bool = CONCURRENT,
) -> AsyncIterator[T]:
    return async_iter(iterators).run_iterators(*ignore_exceptions, concurrent=concurrent).unwrap()


@synchronize
class Client:
    r"""Main class in gd.py, used for interacting with the servers of Geometry Dash.

    Parameters
    ----------
    load_after_post: :class:`bool`
        Whether to load comments/messages/requests after sending them.

        .. note::

            Defaults to ``True``, in which case
            the following method calls will return entities:

            - :meth:`~gd.Client.send_message`;
            - :meth:`~gd.Client.send_friend_request`;
            - :meth:`~gd.Client.comment_level`;
            - :meth:`~gd.Client.post_comment`.

            Otherwise, if ``False`` or not found, these methods will return ``None``.

    \*\*http_args
        Arguments to pass to :class:`~gd.HTTPClient` constructor.

    Attributes
    ----------
    session: :class:`~gd.Session`
        Session used processing requests and responses.

    database: :class:`~gd.api.Database`
        Client's database, used for working with saves.
        There is an alias for it called ``db``.

    account_id: :class:`int`
        Account ID of the client. ``0`` if not logged in.

    id: :class:`int`
        ID of the client. ``0`` if not logged in.

    name: :class:`str`
        Name of the client. Empty string if not logged in.

    password: :class:`str`
        Password of the client. Empty string if not logged in.
    """

    def __init__(self, *, load_after_post: bool = True, **http_args) -> None:
        self.session = Session(**http_args)

        self.load_after_post = load_after_post
        self.listeners: List[AbstractListener] = []
        self.handlers: Dict[str, List[MaybeAsyncFunction]] = {}

        self.database: Database = Database()

        self.account_id = 0
        self.id = 0

        self.name: str = ""
        self.password: str = ""

    def __repr__(self) -> str:
        info = {
            "account_id": self.account_id,
            "name": self.name,
            "id": self.id,
            "session": self.session,
        }

        return make_repr(self, info)

    def edit(self, **attrs) -> "Client":
        r"""Edit attributes of the client.

        Parameters
        ----------
        \*\*attrs
            Attributes to add.

        Returns
        -------
        :class:`~gd.Client`
            Current client.
        """
        for name, value in attrs.items():
            setattr(self, name, value)

        return self

    def is_logged(self) -> bool:
        """Check wether the client is logged in.

        Returns
        -------
        :class:`bool`
            ``True`` if client is logged in, ``False`` otherwise.
        """
        return bool(self.account_id and self.id and self.name and self.password)

    @overload  # noqa
    def run(self, maybe_awaitable: Awaitable[T]) -> T:  # noqa
        ...

    @overload  # noqa
    def run(self, maybe_awaitable: T) -> T:  # noqa
        ...

    def run(self, maybe_awaitable: MaybeAwaitable[T]) -> T:  # noqa
        """Run given maybe awaitable object and return the result.

        Parameters
        ----------
        maybe_awaitable: Union[Awaitable[``T``], ``T``]
            Maybe awaitable object to execute.

        Returns
        -------
        ``T``
            Result of the execution.
        """
        return get_not_running_loop().run_until_complete(maybe_await(maybe_awaitable))

    @property
    def db(self) -> Database:
        """:class:`~gd.api.Database`: Same as :attr:`~gd.Client.database`."""
        return self.database

    @db.setter
    def db(self, database: Database) -> None:
        self.database = database

    @property
    def http(self) -> HTTPClient:
        """:class:`~gd.HTTPClient`: Same as :attr:`gd.Session.http`."""
        return self.session.http

    @property  # type: ignore
    @cache_by("password")
    def encoded_password(self) -> str:
        """:class:`str`: Encoded password for the client."""
        return encode_robtop_str(self.password, Key.ACCOUNT_PASSWORD)  # type: ignore

    @property  # type: ignore
    @login_check
    def user(self) -> User:
        """:class:`~gd.User`: User representing current client."""
        return User(account_id=self.account_id, id=self.id, name=self.name, client=self)

    async def ping_server(self) -> float:
        return await self.ping(self.http.url)

    async def ping(self, url: Union[str, URL]) -> float:
        return await self.session.ping(url)

    async def logout(self) -> None:
        """Logout from account.

        Example
        -------
        >>> await client.login("user", "password")
        >>> await client.logout()
        >>> client.id
        0
        """
        self.database = Database()

        self.account_id = 0
        self.id = 0

        self.name = ""
        self.password = ""

    def login(self, name: str, password: str) -> "LoginContextManager":
        """:async-with:

        Return context manager that can be used to temporarily log in,
        logging out on exit.

        Awaiting on the context manager will act the same as actually logging in.

        Example
        -------
        >>> async with client.login("user", "password"):
        ...     async for friend in client.get_friends():
        ...         print(friend)

        Parameters
        ----------
        name: :class:`str`
            Name of an account.

        password: :class:`str`
            Password of an account.
        """
        return LoginContextManager(self, name, password, unsafe=False)

    async def do_login(self, name: str, password: str) -> None:
        """Login into an account and update client's settings.

        Example
        -------
        >>> await client.do_login("user", "password")
        >>> client.name
        "user"
        >>> client.password
        "password"

        Parameters
        ----------
        name: :class:`str`
            Name of an account.

        password: :class:`str`
            Password of an account.
        """
        model = await self.session.login(name, password)

        log.info("Logged in as %r.", name)

        self.edit(account_id=model.account_id, id=model.id, name=name, password=password)

    def unsafe_login(self, name: str, password: str) -> "LoginContextManager":
        """:async-with:

        Return context manager that can be used to temporarily log in *unsafely*,
        logging out on exit.

        Awaiting on the context manager will act the same as actually logging in.

        Example
        -------
        >>> await client.unsafe_login("user", "password")
        >>> client.name
        "user"
        >>> client.password
        "password"

        Parameters
        ----------
        name: :class:`str`
            Name of an account.

        password: :class:`str`
            Password of an account.
        """
        return LoginContextManager(self, name, password, unsafe=True)

    async def do_unsafe_login(self, name: str, password: str) -> None:
        """Login into an account and update client's settings.

        This function is not *safe*, because it does not use login endpoint.

        Instead, it assumes that credentials are correct,
        and only searches for ID and Account ID.

        Example
        -------
        >>> await client.do_unsafe_login("user", "password")
        >>> client.name
        "user"
        >>> client.password
        "password"

        Parameters
        ----------
        name: :class:`str`
            Name of an account.

        password: :class:`str`
            Password of an account.
        """
        user = await self.search_user(name, simple=True)

        log.info("Logged in? as %r.", name)

        self.edit(name=name, password=password, account_id=user.account_id, id=user.id)

    @login_check
    async def load(self) -> Database:
        """Load cloud save and process it.

        This returns a :class:`~gd.api.Database`, and sets ``client.database`` to it.

        Example
        -------
        >>> await client.login("user", "password")
        >>> database = await client.load()  # load current save
        >>> print(database.user_name)  # print current user name

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to load the save.

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.

        Returns
        -------
        :class:`~gd.api.Database`
            Loaded database.
        """
        database = await self.session.load(
            account_id=self.account_id, name=self.name, password=self.password
        )

        self.database = database

        return database

    @login_check
    async def save(self, database: Optional[Database] = None) -> None:
        """Send save to the cloud.

        Example
        -------
        >>> await client.login("user", "password")
        >>> await client.load()  # load current save
        >>> client.database.set_bootups(0)  # set "bootups" value to "0"
        >>> await client.save()

        Parameters
        ----------
        database: Optional[:class:`~gd.api.Database`]
            Database to save. If not given or ``None``, tries to use :attr:`~gd.Client.database`.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to save the database, or it is empty (i.e. not changed).

        :exc:`~gd.HTTPStatusError`
            Server returned error status code.

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        if database is None:
            if self.database.is_empty():
                raise MissingAccess("No database to save.")

            database = self.database

        await self.session.save(
            database, account_id=self.account_id, name=self.name, password=self.password
        )

    async def get_account_url(self, account_id: int, type: AccountURLType) -> URL:
        return await self.session.get_account_url(account_id=account_id, type=type)

    @login_check
    async def update_profile(
        self,
        stars: Optional[int] = None,
        diamonds: Optional[int] = None,
        coins: Optional[int] = None,
        user_coins: Optional[int] = None,
        demons: Optional[int] = None,
        icon_type: Optional[Union[int, str, IconType]] = None,
        icon: Optional[int] = None,
        color_1_id: Optional[int] = None,
        color_2_id: Optional[int] = None,
        has_glow: Optional[bool] = None,
        cube: Optional[int] = None,
        ship: Optional[int] = None,
        ball: Optional[int] = None,
        ufo: Optional[int] = None,
        wave: Optional[int] = None,
        robot: Optional[int] = None,
        spider: Optional[int] = None,
        death_effect: Optional[int] = None,
        special: int = 0,
        *,
        set_as_user: Optional[User] = None,
    ) -> None:
        """Update profile of the client.

        Example
        -------
        >>> await client.update_profile(has_glow=True)  # enable glow outline

        Parameters
        ----------
        stars: Optional[:class:`int`]
            Amount of stars to set.

        diamonds: Optional[:class:`int`]
            Amount of diamonds to set.

        coins: Optional[:class:`int`]
            Amount of coins to set.

        user_coins: Optional[:class:`int`]
            Amount of user coins to set.

        demons: Optional[:class:`int`]
            Amount of demons to set.

        icon_type: Optional[Union[:class:`int`, :class:`str`, :class:`~gd.IconType`]]
            Icon type to use. See :class:`~gd.IconType` for more info.

        icon: Optional[:class:`int`]
            Icon ID to set.

        color_1_id: Optional[:class:`int`]
            ID of primary color to use.

        color_2_id: Optional[:class:`int`]
            ID of secondary color to use.

        has_glow: Optional[:class:`bool`]
            Whether to use glow outline.

        cube: Optional[:class:`int`]
            ID of cube to use.

        ship: Optional[:class:`int`]
            ID of ship to use.

        ball: Optional[:class:`int`]
            ID of ball to use.

        ufo: Optional[:class:`int`]
            ID of ufo to use.

        wave: Optional[:class:`int`]
            ID of wave to use.

        robot: Optional[:class:`int`]
            ID of robot to use.

        spider: Optional[:class:`int`]
            ID of spider to use.

        death_effect: Optional[:class:`int`]
            ID of death effect to use.

        special: :class:`int`
            Special number to use. Default is ``0``.

        set_as_user: Optional[:class:`~gd.User`]
            User to get all missing parameters from.
            If not given or ``None``, :attr:`~gd.Client.user` is used, which implies that::

                await client.update_profile()

            Will cause no effect.
        """
        if set_as_user is None:
            user = await self.get_user(self.account_id)

        else:
            user = set_as_user

        await self.session.update_profile(
            stars=value_or(stars, user.stars),
            diamonds=value_or(diamonds, user.diamonds),
            coins=value_or(coins, user.coins),
            user_coins=value_or(user_coins, user.user_coins),
            demons=value_or(demons, user.demons),
            icon_type=IconType.from_value(value_or(icon_type, user.icon_type)),
            icon=value_or(icon, user.icon),
            color_1_id=value_or(color_1_id, user.color_1_id),
            color_2_id=value_or(color_2_id, user.color_2_id),
            has_glow=bool(value_or(has_glow, user.has_glow())),
            cube=value_or(cube, user.cube),
            ship=value_or(ship, user.ship),
            ball=value_or(ball, user.ball),
            ufo=value_or(ufo, user.ufo),
            wave=value_or(wave, user.wave),
            robot=value_or(robot, user.robot),
            spider=value_or(spider, user.spider),
            death_effect=value_or(death_effect, user.death_effect),
            special=special,
            account_id=self.account_id,
            name=self.name,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def update_settings(
        self,
        message_state: Optional[Union[int, str, MessageState]] = None,
        friend_request_state: Optional[Union[int, str, FriendRequestState]] = None,
        comment_state: Optional[Union[int, str, CommentState]] = None,
        youtube: Optional[str] = None,
        twitter: Optional[str] = None,
        twitch: Optional[str] = None,
        *,
        set_as_user: Optional[User] = None,
    ) -> None:
        """Update profile of the client.

        Example
        -------
        >>> await client.update_settings(comment_state="open_to_all")  # open comments to everyone

        Parameters
        ----------
        message_state: Optional[Union[:class:`int`, :class:`str`, :class:`~gd.MessageState`]]
            Message state to set. See :class:`~gd.MessageState`.

        friend_request_state: Optional[Union[\
            :class:`int`, :class:`str`, :class:`~gd.FriendRequestState`]]
            Friend request state to set. See :class:`~gd.FriendRequestState`.

        comment_state: Optional[Union[:class:`int`, :class:`str`, :class:`~gd.CommentState`]]
            Comment state to set. See :class:`~gd.CommentState`.

        youtube: Optional[:class:`str`]
            YouTube channel ID to set. In link: ``https://youtube.com/channel/{youtube}``.

        twitter: Optional[:class:`str`]
            Twitter ID to set. In link: ``https://twitter.com/{twitter}``.

        twitch: Optional[:class:`str`]
            Twitch ID to set. In link ``https://twitch.tv/{twitch}``.

        set_as_user: Optional[:class:`~gd.User`]
            User to get all missing parameters from.
            If not given or ``None``, :attr:`~gd.Client.user` is used, which implies that::

                await client.update_settings()

            Will cause no effect.
        """
        if set_as_user is None:
            user = await self.get_user(self.account_id, simple=True)

        else:
            user = set_as_user

        await self.session.update_settings(
            message_state=MessageState.from_value(value_or(message_state, user.message_state)),
            friend_request_state=FriendRequestState.from_value(
                value_or(friend_request_state, user.friend_request_state)
            ),
            comment_state=CommentState.from_value(value_or(comment_state, user.comment_state)),
            youtube=value_or(youtube, user.youtube),
            twitter=value_or(twitter, user.twitter),
            twitch=value_or(twitch, user.twitch),
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    async def get_user(
        self, account_id: int, simple: bool = False, friend_state: bool = False
    ) -> User:
        if friend_state:  # if we need to find friend state
            login_check_object(self)  # assert client is logged in

            profile_model = await self.session.get_user_profile(  # request profile
                account_id,
                client_account_id=self.account_id,
                encoded_password=self.encoded_password,
            )

        else:  # otherwise, just request normally
            profile_model = await self.session.get_user_profile(account_id)

        if simple:  # if only profile is needed, return right away
            return User.from_model(profile_model, client=self)

        search_model = await self.session.search_user(profile_model.id)  # search by ID

        return User.from_models(search_model, profile_model, client=self)

    async def search_user(
        self, query: Union[int, str], simple: bool = False, friend_state: bool = False
    ) -> User:
        search_model = await self.session.search_user(query)  # search using query

        if simple:  # if only simple is required, return right away
            return User.from_model(search_model, client=self)

        if friend_state:  # if friend state is requested
            login_check_object(self)  # assert client is logged in

            profile_model = await self.session.get_user_profile(  # request profile
                search_model.account_id,
                client_account_id=self.account_id,
                encoded_password=self.encoded_password,
            )

        else:  # otherwise, request normally
            profile_model = await self.session.get_user_profile(search_model.account_id)

        return User.from_models(search_model, profile_model, client=self)

    @awaitable_iterator
    async def search_users_on_page(
        self, query: Union[int, str], page: int = 0
    ) -> AsyncIterator[User]:
        response_model = await self.session.search_users_on_page(query, page=page)

        for model in response_model.users:
            yield User.from_model(model, client=self)

    @awaitable_iterator
    def search_users(
        self, query: Union[int, str], pages: Iterable[int] = PAGES, concurrent: bool = CONCURRENT,
    ) -> AsyncIterator[User]:
        return run_async_iterators(
            (self.search_users_on_page(query=query, page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    @awaitable_iterator
    @login_check
    async def get_relationships(
        self, type: Union[int, str, SimpleRelationshipType]
    ) -> AsyncIterator[User]:
        try:
            response_model = await self.session.get_relationships(
                SimpleRelationshipType.from_value(type),
                account_id=self.account_id,
                encoded_password=self.encoded_password,
            )

        except NothingFound:
            return

        for model in response_model.users:
            yield User.from_model(model, client=self)

    @login_check
    def get_friends(self) -> AsyncIterator[User]:
        return self.get_relationships(SimpleRelationshipType.FRIENDS)

    @login_check
    def get_blocked(self) -> AsyncIterator[User]:
        return self.get_relationships(SimpleRelationshipType.BLOCKED)

    @awaitable_iterator
    async def get_top(
        self, strategy: Union[int, str, LeaderboardStrategy], amount: int = 100
    ) -> AsyncIterator[User]:
        response_model = await self.session.get_top(
            LeaderboardStrategy.from_value(strategy),
            amount,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

        for model in response_model.users:
            yield User.from_model(model, client=self)

    get_leaderboard = get_top

    def levels_from_model(self, response_model: LevelSearchResponseModel) -> Iterator[Level]:
        songs = (Song.from_model(model, custom=True, client=self) for model in response_model.songs)
        creators = (User.from_model(model, client=self) for model in response_model.creators)

        id_to_song = {song.id: song for song in songs}
        id_to_creator = {creator.id: creator for creator in creators}

        for model in response_model.levels:
            song = id_to_song.get(model.custom_song_id)

            if song is None:
                song = Song.official(model.official_song_id, server_style=True, client=self)

            creator = id_to_creator.get(model.creator_id)

            if creator is None:
                creator = User(account_id=0, name="unknown", id=model.creator_id, client=self)

            yield Level.from_model(model, creator=creator, song=song, client=self)

    async def get_daily(self, use_client: bool = False) -> Level:
        return await self.get_level(DAILY, use_client=use_client)

    async def get_weekly(self, use_client: bool = False) -> Level:
        return await self.get_level(WEEKLY, use_client=use_client)

    async def get_level(
        self, level_id: int, get_data: bool = True, use_client: bool = False
    ) -> Level:
        if level_id < 0:
            get_data = True

            timely_model = await self.session.get_timely_info(
                bool(~level_id)  # -1 -> 0; -2 -> 1; then call bool
            )

        else:
            timely_model = None

        level_model = None

        if get_data:
            if use_client:
                login_check_object(self)  # assert client is logged in

                download_model = await self.session.download_level(
                    level_id, account_id=self.account_id, encoded_password=self.encoded_password
                )

            else:
                download_model = await self.session.download_level(level_id)

            level_model = download_model.level

            level_id = level_model.id

        level: Level = await self.search_levels_on_page(query=level_id).next()

        if level_model is not None:
            level.options.update(
                Level.from_model(
                    level_model,
                    creator=level.creator,
                    song=level.song,
                    type=level.type,
                    timely_id=level.timely_id,
                    cooldown=level.cooldown,
                    client=self,
                ).options
            )

        if timely_model is not None:
            level.options.update(
                timely_id=timely_model.timely_id,
                type=timely_model.type,
                cooldown=timely_model.cooldown,
            )

        return level

    @awaitable_iterator
    async def search_levels_on_page(
        self,
        query: Optional[Union[int, str, Iterable[Any]]] = None,
        page: int = 0,
        filters: Optional[Filters] = None,
        user: Optional[Union[int, User]] = None,
        gauntlet: Optional[int] = None,
    ) -> AsyncIterator[Level]:
        if user is None:
            user_id = None

        elif isinstance(user, User):
            user_id = user.id

        else:
            user_id = user

        try:
            response_model = await self.session.search_levels_on_page(
                query,
                page,
                filters,
                user_id,
                gauntlet,
                client_account_id=self.account_id,
                client_user_id=self.id,
                encoded_password=self.encoded_password,
            )

        except NothingFound:
            return

        for level in self.levels_from_model(response_model):
            yield level

    @awaitable_iterator
    def search_levels(
        self,
        query: Optional[Union[int, str]] = None,
        pages: Iterable[int] = PAGES,
        filters: Optional[Filters] = None,
        user: Optional[Union[int, User]] = None,
        gauntlet: Optional[int] = None,
        concurrent: bool = CONCURRENT,
    ) -> AsyncIterator[Level]:
        return run_async_iterators(
            (
                self.search_levels_on_page(
                    query=query, page=page, filters=filters, user=user, gauntlet=gauntlet,
                )
                for page in pages
            ),
            ClientException,
            concurrent=concurrent,
        )

    @login_check
    async def update_level_description(self, level: Level, description: Optional[str]) -> None:
        if description is None:
            description = ""

        return await self.session.update_level_description(
            level.id,
            description,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    async def upload_level(
        self,
        name: str = "Unnamed",
        id: int = 0,
        version: int = 1,
        length: Union[int, str, LevelLength] = LevelLength.TINY,
        track_id: int = 0,
        description: str = "",
        song_id: int = 0,
        is_auto: bool = False,
        original: int = 0,
        two_player: bool = False,
        objects: int = 0,
        coins: int = 0,
        stars: int = 0,
        unlisted: bool = False,
        friends_only: bool = False,
        low_detail_mode: bool = False,
        password: Optional[Union[int, str]] = None,
        copyable: bool = False,
        recording: Iterable[RecordingEntry] = (),
        editor_seconds: int = 0,
        copies_seconds: int = 0,
        data: str = "",
        load: bool = True,
    ) -> Level:
        level_id = await self.session.upload_level(
            name=name,
            id=id,
            version=version,
            length=LevelLength.from_value(length),
            track_id=track_id,
            description=description,
            song_id=song_id,
            is_auto=is_auto,
            original=original,
            two_player=two_player,
            objects=objects,
            coins=coins,
            stars=stars,
            unlisted=unlisted,
            friends_only=friends_only,
            low_detail_mode=low_detail_mode,
            password=password,
            copyable=copyable,
            recording=recording,
            editor_seconds=editor_seconds,
            copies_seconds=copies_seconds,
            data=data,
            account_id=self.account_id,
            account_name=self.name,
            encoded_password=self.encoded_password,
        )

        if load:
            return await self.get_level(level_id)

        return Level(id=level_id, client=self)

    async def report_level(self, level: Level) -> None:
        return await self.session.report_level(level.id)

    @login_check
    async def delete_level(self, level: Level) -> None:
        return await self.session.delete_level(
            level.id, account_id=self.account_id, encoded_password=self.encoded_password
        )

    @login_check
    async def rate_level(self, level: Level, stars: int) -> None:
        return await self.session.rate_level(
            level.id, stars, account_id=self.account_id, encoded_password=self.encoded_password,
        )

    @login_check
    async def rate_demon(
        self, level: Level, rating: Union[int, str, DemonDifficulty], as_mod: bool = False,
    ) -> None:
        return await self.session.rate_demon(
            level.id,
            DemonDifficulty.from_value(rating),
            as_mod=as_mod,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def send_level(self, level: Level, stars: int, feature: bool) -> None:
        return await self.session.rate_level(  # type: ignore
            level.id,
            stars,
            feature,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @awaitable_iterator
    @login_check
    async def get_level_top(
        self,
        level: Level,
        strategy: Union[int, str, LevelLeaderboardStrategy] = LevelLeaderboardStrategy.ALL,
    ) -> AsyncIterator[User]:
        response_model = await self.session.get_level_top(
            level.id,
            LevelLeaderboardStrategy.from_value(strategy),
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

        for model in response_model.users:
            yield User.from_model(model, client=self)

    get_level_leaderboard = get_level_top

    @login_check
    async def block(self, user: User) -> None:
        return await self.session.block_or_unblock(
            user.account_id,
            unblock=False,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def unblock(self, user: User) -> None:
        return await self.session.block_or_unblock(
            user.account_id,
            unblock=True,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def unfriend(self, user: User) -> None:
        return await self.session.unfriend_user(
            user.account_id,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def send_message(
        self, user: User, subject: Optional[str] = None, content: Optional[str] = None
    ) -> Optional[Message]:
        await self.session.send_message(
            account_id=user.account_id,
            subject=subject,
            content=content,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

        if self.load_after_post:
            if subject is None:
                subject = ""

            if content is None:
                content = ""

            messages = self.get_messages_on_page(type=MessageType.OUTGOING)
            message = await messages.get(subject=subject, recipient=user)

            if message is None:
                return None

            message.content = content

            return message

        return None

    @login_check
    async def get_message(self, message_id: int, type: MessageType) -> Message:
        model = await self.session.download_message(
            message_id,
            type=type,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )
        return Message.from_model(model, other_user=self.user, type=type, client=self)

    @login_check
    async def read_message(self, message: Message) -> str:
        read = await self.get_message(message.id, message.type)
        return read.content

    @login_check
    async def delete_message(self, message: Message) -> None:
        return await self.session.delete_message(
            message.id,
            type=message.type,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @awaitable_iterator
    @login_check
    async def get_messages_on_page(
        self, type: Union[int, str, MessageType] = MessageType.INCOMING, page: int = 0
    ) -> AsyncIterator[Message]:
        message_type = MessageType.from_value(type)

        try:
            response_model = await self.session.get_messages_on_page(
                message_type,
                page,
                account_id=self.account_id,
                encoded_password=self.encoded_password,
            )

        except NothingFound:
            return

        for model in response_model.messages:
            yield Message.from_model(model, client=self, other_user=self.user, type=message_type)

    @awaitable_iterator
    @login_check
    def get_messages(
        self,
        type: Union[int, str, MessageType] = MessageType.INCOMING,
        pages: Iterable[int] = PAGES,
        concurrent: bool = CONCURRENT,
    ) -> AsyncIterator[Message]:
        return run_async_iterators(
            (self.get_messages_on_page(type=type, page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    @login_check
    async def send_friend_request(
        self, user: User, message: Optional[str] = None
    ) -> Optional[FriendRequest]:
        await self.session.send_friend_request(
            account_id=user.account_id,
            message=message,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

        if self.load_after_post:
            if message is None:
                message = ""

            friend_requests = self.get_friend_requests_on_page(type=FriendRequestType.OUTGOING)
            friend_request = await friend_requests.get(recipient=user)

            if friend_request is None:
                return None

            return friend_request

        return None

    @login_check
    async def delete_friend_request(self, friend_request: FriendRequest) -> None:
        return await self.session.delete_friend_request(
            account_id=friend_request.author.account_id,
            type=friend_request.type,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def accept_friend_request(self, friend_request: FriendRequest) -> None:
        return await self.session.accept_friend_request(
            account_id=friend_request.author.account_id,
            request_id=friend_request.id,
            type=friend_request.type,
            client_account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def read_friend_request(self, friend_request: FriendRequest) -> None:
        return await self.session.read_friend_request(
            request_id=friend_request.id,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @awaitable_iterator
    @login_check
    async def get_friend_requests_on_page(
        self, type: Union[int, str, FriendRequestType] = FriendRequestType.INCOMING, page: int = 0,
    ) -> AsyncIterator[FriendRequest]:
        friend_request_type = FriendRequestType.from_value(type)

        try:
            response_model = await self.session.get_friend_requests_on_page(
                friend_request_type,
                page,
                account_id=self.account_id,
                encoded_password=self.encoded_password,
            )

        except NothingFound:
            return

        for model in response_model.friend_requests:
            yield FriendRequest.from_model(
                model, client=self, other_user=self.user, type=friend_request_type
            )

    @awaitable_iterator
    @login_check
    def get_friend_requests(
        self,
        type: Union[int, str, FriendRequestType] = FriendRequestType.INCOMING,
        pages: Iterable[int] = PAGES,
        concurrent: bool = CONCURRENT,
    ) -> AsyncIterator[FriendRequest]:
        return run_async_iterators(
            (self.get_friend_requests_on_page(type=type, page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    @login_check
    async def like(self, entity: Union[Comment, Level]) -> None:
        return await self.like_or_dislike(entity, dislike=False)

    @login_check
    async def dislike(self, entity: Union[Comment, Level]) -> None:
        return await self.like_or_dislike(entity, dislike=True)

    @login_check
    async def like_or_dislike(self, entity: Union[Comment, Level], dislike: bool) -> None:
        if isinstance(entity, Comment):
            if entity.type is CommentType.LEVEL:
                like_type, special_id = LikeType.LEVEL_COMMENT, entity.level_id
            else:
                like_type, special_id = LikeType.COMMENT, entity.id

        elif isinstance(entity, Level):
            like_type, special_id = LikeType.LEVEL, 0

        else:
            raise TypeError(f"Expected Comment or User, got {type(entity).__name__!r}.")

        return await self.session.like_or_dislike(
            type=like_type,  # type: ignore
            item_id=entity.id,
            special_id=special_id,
            dislike=dislike,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @login_check
    async def comment_level(
        self, level: Level, content: Optional[str] = None, percent: int = 0
    ) -> Optional[Comment]:
        await self.session.post_comment(
            type=CommentType.LEVEL,  # type: ignore
            content=content,
            level_id=level.id,
            percent=percent,
            account_id=self.account_id,
            account_name=self.name,
            encoded_password=self.encoded_password,
        )

        if self.load_after_post:
            if content is None:
                content = ""

            comments = self.get_level_comments_on_page(level)
            comment = await comments.get(author=self.user, content=content)

            if comment is None:
                return None

            return comment

        return None

    @login_check
    async def post_comment(self, content: Optional[str] = None) -> Optional[Comment]:
        await self.session.post_comment(
            type=CommentType.PROFILE,  # type: ignore
            content=content,
            level_id=0,
            percent=0,
            account_id=self.account_id,
            account_name=self.name,
            encoded_password=self.encoded_password,
        )

        if self.load_after_post:
            if content is None:
                content = ""

            comments = self.get_user_comments_on_page(type=CommentType.PROFILE)
            comment = await comments.get(author=self.user, content=content)

            if comment is None:
                return None

            return comment

        return None

    @login_check
    async def delete_comment(self, comment: Comment) -> None:
        return await self.session.delete_comment(
            comment_id=comment.id,
            type=comment.type,
            level_id=comment.level_id,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )

    @awaitable_iterator
    async def get_user_comments_on_page(
        self,
        user: User,
        type: Union[int, str, CommentType] = CommentType.PROFILE,
        page: int = 0,
        *,
        strategy: Union[int, str, CommentStrategy] = CommentStrategy.RECENT,
    ) -> AsyncIterator[Comment]:
        response_model = await self.session.get_user_comments_on_page(
            account_id=user.account_id,
            user_id=user.id,
            type=CommentType.from_value(type),
            page=page,
            strategy=CommentStrategy.from_value(strategy),
        )

        for model in response_model.comments:
            yield Comment.from_model(model, client=self, user=user)

    @awaitable_iterator
    def get_user_comments(
        self,
        user: User,
        type: Union[int, str, CommentType] = CommentType.PROFILE,
        pages: Iterable[int] = PAGES,
        *,
        strategy: Union[int, str, CommentStrategy] = CommentStrategy.RECENT,
        concurrent: bool = CONCURRENT,
    ) -> AsyncIterator[Comment]:
        return run_async_iterators(
            (
                self.get_user_comments_on_page(user=user, type=type, page=page, strategy=strategy)
                for page in pages
            ),
            ClientException,
            concurrent=concurrent,
        )

    @awaitable_iterator
    async def get_level_comments_on_page(
        self,
        level: Level,
        amount: int = COMMENT_PAGE_SIZE,
        page: int = 0,
        *,
        strategy: Union[int, str, CommentStrategy] = CommentStrategy.RECENT,
    ) -> AsyncIterator[Comment]:
        try:
            response_model = await self.session.get_level_comments_on_page(
                level_id=level.id,
                amount=amount,
                page=page,
                strategy=CommentStrategy.from_value(strategy),
            )

        except NothingFound:
            return

        for model in response_model.comments:
            yield Comment.from_model(model, client=self)

    @awaitable_iterator
    def get_level_comments(
        self,
        level: Level,
        amount: int = COMMENT_PAGE_SIZE,
        pages: Iterable[int] = PAGES,
        *,
        strategy: Union[int, str, CommentStrategy] = CommentStrategy.RECENT,
        concurrent: bool = CONCURRENT,
    ) -> AsyncIterator[Comment]:
        return run_async_iterators(
            (
                self.get_level_comments_on_page(
                    level=level, amount=amount, page=page, strategy=strategy
                )
                for page in pages
            ),
            ClientException,
            concurrent=concurrent,
        )

    @awaitable_iterator
    async def get_gauntlets(self) -> AsyncIterator[Gauntlet]:
        response_model = await self.session.get_gauntlets()

        for model in response_model.gauntlets:
            yield Gauntlet.from_model(model, client=self)

    @awaitable_iterator
    async def get_map_packs_on_page(self, page: int = 0) -> AsyncIterator[MapPack]:
        response_model = await self.session.get_map_packs_on_page(page=page)

        for model in response_model.map_packs:
            yield MapPack.from_model(model, client=self)

    @awaitable_iterator
    def get_map_packs(
        self, pages: Iterable[int] = PAGES, concurrent: bool = CONCURRENT
    ) -> AsyncIterator[MapPack]:
        return run_async_iterators(
            (self.get_map_packs_on_page(page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    @awaitable_iterator
    @login_check
    async def get_quests(self) -> AsyncIterator[Quest]:
        response_model = await self.session.get_quests(
            account_id=self.account_id, encoded_password=self.encoded_password
        )
        model = response_model.inner

        for quest_model in (model.quest_1, model.quest_2, model.quest_3):

            yield Quest.from_model(quest_model, seconds=model.time_left, client=self)

    @awaitable_iterator
    @login_check
    async def get_chests(
        self,
        reward_type: RewardType = RewardType.GET_INFO,  # type: ignore
        chest_1_count: int = 0,
        chest_2_count: int = 0,
    ) -> AsyncIterator[Chest]:
        response_model = await self.session.get_chests(
            reward_type=reward_type,
            chest_1_count=chest_1_count,
            chest_2_count=chest_2_count,
            account_id=self.account_id,
            encoded_password=self.encoded_password,
        )
        model = response_model.inner

        for (chest_model, time_left, count) in (
            (model.chest_1, model.chest_1_left, model.chest_1_count),
            (model.chest_2, model.chest_2_left, model.chest_2_count),
        ):
            yield Chest.from_model(chest_model, seconds=time_left, count=count, client=self)

    @awaitable_iterator
    async def get_featured_artists_on_page(self, page: int = 0) -> AsyncIterator[Song]:
        response_model = await self.session.get_featured_artists_on_page(page=page)

        for model in response_model.featured_artists:
            yield Song.from_model(model, custom=True, client=self)

    @awaitable_iterator
    def get_featured_artists(
        self, pages: Iterable[int] = PAGES, concurrent: bool = CONCURRENT
    ) -> AsyncIterator[MapPack]:
        return run_async_iterators(
            (self.get_featured_artists_on_page(page=page) for page in pages),  # type: ignore
            ClientException,
            concurrent=concurrent,
        )

    async def get_song(self, song_id: int) -> Song:
        model = await self.session.get_song(song_id)
        return Song.from_model(model, custom=True, client=self)

    async def get_ng_song(self, song_id: int) -> Song:
        model = await self.session.get_ng_song(song_id)
        return Song.from_model(model, custom=True, client=self)

    async def get_artist_info(self, song_id: int) -> ArtistInfo:
        artist_info = await self.session.get_artist_info(song_id)
        return ArtistInfo.from_dict(artist_info, client=self)  # type: ignore

    @awaitable_iterator
    async def search_ng_songs_on_page(self, query: str, page: int = 0) -> AsyncIterator[Song]:
        models = await self.session.search_ng_songs_on_page(query=query, page=page)

        for model in models:
            yield Song.from_model(model, custom=True, client=self)

    @awaitable_iterator
    def search_ng_songs(
        self, query: str, pages: Iterable[int] = PAGES, concurrent: bool = CONCURRENT
    ) -> AsyncIterator[Song]:
        return run_async_iterators(
            (self.search_ng_songs_on_page(query=query, page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    @awaitable_iterator
    async def search_ng_users_on_page(self, query: str, page: int = 0) -> AsyncIterator[Author]:
        data = await self.session.search_ng_users_on_page(query=query, page=page)

        for part in data:
            yield Author.from_dict(part, client=self)  # type: ignore

    @awaitable_iterator
    def search_ng_users(
        self, query: str, pages: Iterable[int] = PAGES, concurrent: bool = CONCURRENT
    ) -> AsyncIterator[Author]:
        return run_async_iterators(
            (self.search_ng_users_on_page(query=query, page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    @awaitable_iterator
    async def get_ng_user_songs_on_page(self, name: str, page: int = 0) -> AsyncIterator[Song]:
        models = await self.session.get_ng_user_songs_on_page(name=name, page=page)

        for model in models:
            yield Song.from_model(model, custom=True, client=self)

    @awaitable_iterator
    def get_ng_user_songs(
        self, name: str, pages: Iterable[int] = PAGES, concurrent: bool = CONCURRENT
    ) -> AsyncIterator[Song]:
        return run_async_iterators(
            (self.get_ng_user_songs_on_page(name=name, page=page) for page in pages),
            ClientException,
            concurrent=concurrent,
        )

    async def on_daily(self, level: Level) -> T:
        """This is the event that is fired when a new daily level is set.
        See :ref:`events` for more info.
        """
        pass

    async def on_weekly(self, level: Level) -> T:
        """This is the event that is fired when a new weekly demon is assigned.
        See :ref:`events` for more info.
        """
        pass

    async def on_rate(self, level: Level) -> T:
        """This is the event that is fired when a new level is rated.
        See :ref:`events` for more info.
        """
        pass

    async def on_unrate(self, level: Level) -> T:
        """This is the event that is fired when a level is unrated.
        See :ref:`events` for more info.
        """
        pass

    async def on_message(self, message: Message) -> T:
        """This is the event that is fired when a logged in client gets a message.
        See :ref:`events` for more info.
        """
        pass

    async def on_friend_request(self, friend_request: FriendRequest) -> T:
        """This is the event that is fired when a logged in client gets a friend request.
        See :ref:`events` for more info.
        """
        pass

    async def on_level_comment(self, level: Level, comment: Comment) -> T:
        """This is the event that is fired when a comment is posted on some level.
        See :ref:`events` for more info.
        """
        pass

    async def dispatch(self, event_name: str, *args, **kwargs) -> None:
        r"""Dispatch an event given by ``event_name`` with ``*args`` and ``**kwargs``.

        Parameters
        ----------
        event_name: :class:`str`
            Name of event to dispatch without ``on_`` prefix, e.g. ``"new_daily"``.

        \*args
            Args to call handler with.

        \*\*kwargs
            Keyword args to call handler with.
        """
        name = "on_" + event_name

        log.info(f"Dispatching event {event_name!r}, client: {self!r}")

        try:
            method = getattr(self, name)

        except AttributeError:
            pass

        else:
            try:
                await maybe_coroutine(method, *args, **kwargs)

            except Exception:
                traceback.print_exc()

        handlers = self.handlers.get(event_name)

        if handlers is None:
            return

        for handler in handlers:
            try:
                await maybe_coroutine(handler, *args, **kwargs)

            except Exception:
                traceback.print_exc()

    def event(self, function: MaybeAsyncFunction) -> MaybeAsyncFunction:
        """
        A decorator that registers an event to listen to::

            @client.event
            async def on_level_rated(level: gd.Level) -> None:
                print(level.name)
        """
        setattr(self, function.__name__, function)
        log.debug("%s has been successfully registered as an event.", function.__name__)

        return function

    def listen(self, event_name: str) -> Callable[[MaybeAsyncFunction], MaybeAsyncFunction]:
        def inner(function: MaybeAsyncFunction) -> MaybeAsyncFunction:
            self.handlers.setdefault(event_name, []).append(function)
            return function

        return inner

    def create_listener(self, event_name: str, *args, **kwargs) -> AbstractListener:
        listener: AbstractListener

        kwargs.update(client=self)

        if event_name in {"daily", "weekly"}:
            kwargs.update(daily=(event_name == "daily"))
            listener = TimelyLevelListener(*args, **kwargs)

        elif event_name in {"rate", "unrate"}:
            kwargs.update(rate=(event_name == "rate"))
            listener = RateLevelListener(*args, **kwargs)

        elif event_name in {"friend_request", "message"}:
            kwargs.update(message=(event_name == "message"))
            listener = MessageOrRequestListener(*args, **kwargs)

        elif event_name in {"level_comment"}:
            listener = LevelCommentListener(*args, **kwargs)

        elif event_name in {"user_comment"}:
            listener = UserCommentListener(*args, **kwargs)

        else:
            raise TypeError(f"Invalid listener type: {type!r}.")

        return listener

    def apply_listener(self, event_name: str, *args, **kwargs) -> None:
        self.listeners.append(self.create_listener(event_name, *args, **kwargs))

    def listen_for(
        self, event_name: str, *args, **kwargs
    ) -> Callable[[MaybeAsyncFunction], MaybeAsyncFunction]:
        self.apply_listener(event_name, *args, **kwargs)
        return self.listen(event_name)


class LoginContextManager:
    def __init__(self, client: Client, user: str, password: str, unsafe: bool = False) -> None:
        self._client = client
        self._user = user
        self._password = password
        self._unsafe = unsafe

    @property
    def client(self) -> Client:
        return self._client

    @property
    def user(self) -> str:
        return self._user

    @property
    def password(self) -> str:
        return self._password

    @property
    def unsafe(self) -> bool:
        return self._unsafe

    async def login(self) -> None:
        if self.unsafe:
            await self.client.do_unsafe_login(self.user, self.password)

        else:
            await self.client.do_login(self.user, self.password)

    async def logout(self) -> None:
        await self.client.logout()

    def __await__(self) -> Generator[Any, None, None]:
        return self.login().__await__()

    async def __aenter__(self) -> Client:
        await self.login()

        return self.client

    async def __aexit__(
        self, error_type: Type[BaseException], error: BaseException, traceback: types.TracebackType
    ) -> None:
        await self.logout()
