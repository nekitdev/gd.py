import asyncio

import logging
from typing import Union, Sequence

from .session import _session

from .utils.enums import value_to_enum, LeaderboardStrategy, IconType
from .utils.filters import Filters
from .utils.save_parser import Save
from .utils.wrap_tools import make_repr, check

from .utils.crypto.coders import Coder

from . import utils

log = logging.getLogger(__name__)


class Client:
    """A main class in the gd.py library, used for interacting with the servers of Geometry Dash.

    Parameters
    ----------
    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The :class:`asyncio.AbstractEventLoop` to use for asynchronous operations.
        Defaults to ``None``, in which case the default event loop is used
        via :func:`.utils.acquire_loop`.

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
    raw_save: Sequence[Union[:class:`bytes`, :class:`str`]]
        Raw decoded save. If not loaded, defaults to ``()``.
    save: :class:`.Save`
        This is a namedtuple with format ``(completed, followed)``.
        Contains empty lists if not loaded.
    """
    def __init__(self, *, loop=None):
        self.session = _session
        self.loop = loop or utils.acquire_loop()
        self._set_to_defaults()

    def __repr__(self):
        info = {
            'is_logged': self.is_logged(),
            'account_id': self.account_id,
            'id': self.id,
            'name': self.name,
            'password': repr('...')
        }
        return make_repr(self, info)

    def _set_to_defaults(self):
        self.save = Save(completed=[], followed=[])
        self.raw_save = ()
        self.account_id = 0
        self.id = 0
        self.name = None
        self.password = None
        self.encodedpass = None

    def _upd(self, attr, value):
        setattr(self, attr, value)
        # update encodedpass if password was updated
        if attr == 'password':
            self.encodedpass = Coder.encode(type='accountpass', string=self.password)

    def is_logged(self):
        return (self.name is not None) and (self.password is not None)

    async def ping_server(self):
        """|coro|

        Pings ``boomlings.com/database`` and prints the time taken.
        Returns the ping as well.

        Returns
        -------
        :class:`float`
            Server ping, in milliseconds.
        """
        duration = await self.session.ping_server('http://boomlings.com/database/')

        print('GD Server ping: {}ms'.format(duration))

        return duration

    async def get_song(self, song_id: int = 0):
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

    async def get_ng_song(self, song_id: int = 0):
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

    async def get_user(self, account_id: int = 0):
        """|coro|

        Gets a user from Geometry Dash server.

        Parameters
        ----------
        account_id: :class:`int`
            An account ID of the user to fetch.

            .. note::

                If the given ID is equal to -1, a :class:`.UnregisteredUser` will be returned.

        Raises
        ------
        :exc:`.MissingAccess`
            User with given account ID was not found.

        Returns
        -------
        :class:`.User`
            The user from the ID. (if ID != -1)
        """
        return await self.session.get_user(account_id, return_only_stats=False, client=self)

    async def fetch_user(self, account_id: int = 0, *, stats: bool = False):
        """|coro|

        This is almost like :meth:`.Client.get_user`, except that it returns
        either :class:`.UserStats` or :class:`.AbstractUser` object.

        Parameters
        ----------
        account_id: :class:`int`
            An account ID of the user to fetch stats of.

            .. note::

                If the given ID is equal to -1, a :class:`.UnregisteredUser` will be returned.

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

    async def search_user(self, query: Union[int, str] = None):
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
        Union[:class:`.User`, :class:`.UnregisteredUser`]
            A User found when searching with the query.
        """
        return await self.session.search_user(query, return_abstract=False, client=self)

    async def find_user(self, query: Union[int, str] = None):
        """|coro|

        Fetches a user on Geometry Dash servers by given query.

        Works almost like :meth:`.Client.search_user`, except the fact that
        it returns :class:`.AbstractUser` or :class:`.UnregisteredUser`.

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
        Union[:class:`.AbstractUser`, :class:`.UnregisteredUser`]
            An AbstractUser or UnregisteredUser corresponding to the query.
        """
        return await self.session.search_user(query, return_abstract=True, client=self)

    async def get_daily(self):
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

    async def get_weekly(self):
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

    async def get_level(self, level_id: int = 0):
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

        Raises
        ------
        :exc:`.MissingAccess`
            Level with given ID was not found.

        Returns
        -------
        :class:`.Level`
            The level corresponding to given id.
        """
        return await self.session.get_level(level_id, client=self)

    async def get_many_levels(self, *level_ids: Sequence[int]):
        """|coro|

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

    async def get_gauntlets(self):
        """|coro|

        Fetches *The Lost Gauntlets*.

        Returns
        -------
        List[:class:`.Gauntlet`]
            All gauntlets retrieved, as list.
        """
        return await self.session.get_gauntlets(client=self)

    async def get_page_map_packs(self, page: int = 0, *, raise_errors: bool = True):
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

    async def get_map_packs(self, pages: Sequence[int] = None):
        """|coro|

        Gets map packs on given ``pages``.

        Parameters
        ----------
        pages: Sequence[:class:`int`]
            Pages to search map packs on.

        Returns
        -------
        List[:class:`.MapPack`]
            List of map packs found.
        """
        if pages is None:
            pages = range(10)

        return await self.session.get_map_packs(pages=pages, client=self)

    async def test_captcha(self):
        """|coro|

        Tests Captcha solving.

        Returns
        -------
        :class:`int`
            The code of the Captcha.
        """
        return await self.session.test_captcha()

    async def login(self, user: str, password: str):
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


    @check.is_logged()
    async def upload_level(
        self, name: str = 'Unnamed', id: int = 0, version: int = 1, length: int = 0,
        track: int = 0, song_id: int = 0, is_auto: bool = False, original: int = 0,
        two_player: bool = False, objects: int = None, coins: int = 0, star_amount: int = 0,
        unlist: bool = False, ldm: bool = False, password: int = 0, copyable: bool = False,
        data: str = '', description: str = '', *, load: bool = True
    ):
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
        password: :class:`int`
            The password to apply.
        copyable: :class:`bool`
            Indicates whether the level should be copyable.
        data: :class:`str`
            The data of the level, as a string.
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
            objects = len(data.split(';')) - 2
            objects = 0 if objects < 0 else objects

        return await self.session.upload_level(
            data=data, name=name, level_id=id, version=version, length=length,
            audio_track=track, song_id=song_id, is_auto=is_auto, original=original,
            two_player=two_player, objects=objects, coins=coins, stars=star_amount,
            unlisted=unlist, ldm=ldm, password=password, copyable=copyable,
            desc=description, load_after=load, client=self
        )

    @check.is_logged()
    async def get_page_levels(self, page: int = 0, *, raise_errors: bool = True):
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

    @check.is_logged()
    async def get_levels(self, pages: Sequence[int] = None):
        """|coro|

        Searches for levels on given pages.

        .. note::

            This method requires authorised client.

        Parameters
        ----------
        pages: Sequence[:class:`int`]
            Pages to look for levels at.

        Returns
        -------
        List[:class:`.Level`]
            All levels found, as list, which might be empty.
        """
        filters = Filters.setup_by_user()
        return await self.search_levels(pages=pages, filters=filters)

    @check.is_logged()
    async def load(self):
        """|coro|

        Loads save from a server and parses it.
        Sets :attr:`.Client.save` to :class:`.Save` namedtuple ``(completed, followed)``.
        """
        success = await self.session.load_save(client=self)

        if success:
            log.info('Successfully loaded a save.')
        else:
            log.warning('Failed to load a save.')

    @check.is_logged()
    async def backup(self, save_data: Sequence[Union[bytes, str]] = None):
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
        if save_data is None and not self.raw_save:
            return log.warning('No data was provided.')

        data = save_data if save_data else self.raw_save

        await self.session.do_save(client=self, data=data)

    def close(self, message: str = 'Logged out, no additional description.'):
        """*Closes* client.

        Basically sets its password and username to ``None``, which
        actually implies that client logs out.

        Parameters
        ----------
        message: :class:`str`
            A message to print after closing.
        """
        self._set_to_defaults()

        print(message)

        log.info('Has logged out with message: %r', message)

    @check.is_logged()
    async def get_friends(self):
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
        return await self.session.get_friends(client=self)

    @check.is_logged()
    async def to_user(self):
        """|coro|

        Gets user with :attr:`.Client.account_id`,
        which means that client should be logged in.

        Returns
        -------
        :class:`.User`
            User corresponding to :attr:`.Client.account_id`.
        """
        return await self.get_user(self.account_id)

    @check.is_logged()
    async def get_page_messages(
        self, sent_or_inbox: str = 'inbox', page: int = 0, *, raise_errors: bool = True
    ):
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

    @check.is_logged()
    async def get_messages(
        self, sent_or_inbox: str = 'inbox', pages: Sequence[int] = None
    ):
        """|coro|

        Retrieves messages from given ``pages``.

        Parameters
        ----------
        sent_or_inbox: :class:`str`
            Type of messages to retrieve. Either `'sent'` or `'inbox'`.
            Defaults to the latter.

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.Message`]
            List of messages found. Can be an empty list.
        """
        if pages is None:
            pages = range(10)

        return await self.session.get_messages(
            sent_or_inbox=sent_or_inbox, pages=pages, client=self
        )

    @check.is_logged()
    async def get_page_friend_requests(
        self, sent_or_inbox: str = 'inbox', page: int = 0, *, raise_errors: bool = True
    ):
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

    @check.is_logged()
    async def get_friend_requests(
        self, sent_or_inbox: str = 'inbox', pages: Sequence[int] = None
    ):
        """|coro|

        Retrieves friend requests from given ``pages``.

        Parameters
        ----------
        sent_or_inbox: :class:`str`
            Type of friend requests to retrieve. Either `'sent'` or `'inbox'`.
            Defaults to the latter.

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.FriendRequests`]
            List of friend requests found. Can be an empty list.
        """
        if pages is None:
            pages = range(10)

        return await self.session.get_friend_requests(
            sent_or_inbox=sent_or_inbox, pages=pages, client=self
        )

    @check.is_logged()
    def get_parse_dict(self):
        return {k: getattr(self, k) for k in ('name', 'id', 'account_id')}

    def as_user(self):
        return self.session.to_user(self.get_parse_dict(), client=self)

    async def get_top(self, strategy: Union[int, str, LeaderboardStrategy] = 0, *, count: int = 100):
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


        """
        strategy = value_to_enum(LeaderboardStrategy, strategy)
        return await self.session.get_top(strategy=strategy, count=count, client=self)

    async def get_leaderboard(
        self, strategy: Union[int, str, LeaderboardStrategy] = 0, *, count: int = 100):
        """|coro|

        This is an alias for :meth:`.Client.get_top`.
        """
        return await self.get_top(strategy, count=count)

    @check.is_logged()
    async def post_comment(self, content: str):
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

    @check.is_logged()
    async def edit(self, name: str = None, password: str = None):
        """|coro|

        Tries to edit credentials of a client, if logged in.

        .. note::

            See :meth:`.Client.test_captcha` to see information about how to treat this function.

        Parameters
        ----------
        name: :class:`str`
            A name to change logged account's username to. Defaults to ``None``.

        password: :class:`str`
            A password to change logged account's username to. Defaults to ``None``.

        Raises
        ------
        :exc:`.FailedToChange`
            Failed to change the credentials.
        """
        await self.session.edit(name=name, password=password, client=self)

        # if no errors occured, log changes.
        if name is not None:
            log.debug('Changed username to: %s', name)

        if password is not None:
            log.debug('Changed password to: %s', password)

    @check.is_logged()
    async def update_profile(
        self, stars: int = 0, demons: int = 0, diamonds: int = 0, has_glow: bool = False,
        icon_type: int = 0, color_1: int = 0, color_2: int = 3, coins: int = 0,
        user_coins: int = 0, cube: int = 1, ship: int = 1, ball: int = 1, ufo: int = 1,
        wave: int = 1, robot: int = 1, spider: int = 1, explosion: int = 1, special: int = 0,
        set_as_user=None
    ):
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

    @check.is_logged()
    async def update_settings(
        self, *, msg: int = None, friend_req: int = None, comments: int = None,
        youtube: str = None, twitter: str = None, twitch: str = None
    ):
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
                s = utils.convert_to_type(tmp, int, str)

            args.append(s)

        await self.session.update_settings(*args, client=self)

    async def search_levels_on_page(
        self, page: int = 0, query: str = '', filters: Filters = None, user=None,
        *, raise_errors: bool = True
    ):
        """|coro|

        Searches levels on given page by given query, applying filters as well.

        Parameters
        ----------
        page: :class:`int`
            A page to search levels on.

        query: :class:`int`
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
        ``None`` [yet]
        """
        return await self.session.search_levels_on_page(
            page=page, query=query, filters=filters, user=user, raise_errors=raise_errors, client=self
        )

    async def search_levels(
        self, query: str = '', filters: Filters = None, user=None,
        pages: Sequence[int] = None
    ):
        """|coro|

        Searches levels on given pages.

        Parameters
        ----------
        query: :class:`int`
            A query to search with.

        filters: :class:`.Filters`
            Filters to apply, as an object.

        user: Union[:class:`int`, :class:`.AbstractUser`, :class:`.User`]
            A user to search levels by. (if :class:`.Filters` has parameter ``strategy``
            equal to :class:`.SearchStrategy` ``BY_USER``. Can be omitted, then
            logged in client is required.)

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.Level`]
            List of levels found. Can be an empty list.
        """
        if pages is None:
            pages = range(10)

        return await self.session.search_levels(
            query=query, filters=filters, user=user, pages=pages, client=self
        )

    async def on_new_daily(self, level):
        """|coro|

        This is an event that is fired when a new daily level is set.

        See :ref:`events` for more info.
        """
        pass

    async def on_new_weekly(self, level):
        """|coro|

        This is an event that is fired when a new weekly demon is assigned.

        See :ref:`events` for more info.
        """
        pass

    def run(self, coro, *, debug: bool = False):
        """A handy shortcut for :func:`.utils.run`.

        This is equivalent to:

        .. code-block:: python3

            gd.utils.run(coro, loop=self.loop, debug=debug)
        """
        return utils.run(coro, loop=self.loop, debug=debug)

    def event(self, coro):
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
