import asyncio

import logging
from typing import Union, Sequence

from .session import _session

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
        Defaults to ``None``, in which case the default event loop is used via
        :func:`asyncio.get_event_loop()`.
    """
    def __init__(self, *, loop=None):
        self.session = _session
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self._set_to_defaults()

    def __repr__(self):
        info = {
            'is_logged': self.is_logged()
        }
        return make_repr(self, info)

    def _set_to_defaults(self):
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

        print(f'gd server ping: {duration}ms')

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
            Song was not allowed to use. (Might be deprecated soon)

        Returns
        -------
        :class:`.Song`
            The song from the ID.
        """
        return await self.session.get_song(song_id)

    async def get_ng_song(self, song_id: int = 0):
        """|coro|

        Fetches a song from Newgrounds.

        This function is in most cases faster than :meth:`.Client.get_song`,
        and it does not raise errors if a song is banned on GD Server.

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

        Fetches a user from Geometry Dash server.

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
        return await self.session.get_user(account_id, client=self)

    async def search_user(self, query: Union[int, str] = None):
        """|coro|

        Searches for a user on Geometry Dash servers.

        Parameters
        ----------
        query: Union[:class:`int`, :class:`str`]
            A query to search for user with.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing was found.

        Returns
        -------
        :class:`.AbstractUser`
            An AbstractUser found when searching with the query.
        """
        return await self.session.search_user(query, client=self)

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

    async def test_captcha(self):
        """|coro|

        Tests Captcha solving, and prints the result.

        .. note::

            Captcha is being solved asynchronously.
            It uses :meth:`asyncio.AbstractEventLoop.run_in_executor` method of ``self.loop``,
            which means the following:

            .. code-block:: python3

                import asyncio  # 3.7 and higher
                asyncio.run(client.test_captcha())  # ERROR!

                import gd
                gd.utils.run(client.test_captcha())  # ERROR!

                import gd
                gd.utils.run(client.test_captcha(), loop=client.loop)  # OK

            Please consider what has been said above when writing your programs.
        """
        code = await self.session.test_captcha(client=self)

        print(code)

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
        self, sent_or_inbox: str = 'inbox', pages: Sequence[int] = [],
        *, sort_by_page: bool = True, timeout: Union[int, float] = 5.0
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

        sort_by_page: :class:`bool`
            Indicates whether returned comments should be sorted by page.

        timeout: Union[:class:`int`, :class:`float`]
            Timeout to stop requesting after it occurs.
            Used to prevent insanely long responses.

        Returns
        -------
        List[:class:`.Comment`]
            List of comments found. Can be an empty list.
        """
        return await self.session.get_messages(
            sent_or_inbox=sent_or_inbox, pages=pages, sort_by_page=sort_by_page,
            timeout=timeout, client=self
        )

    @check.is_logged()
    def _get_parse_dict(self):
        return {k: getattr(self, k) for k in ('name', 'id', 'account_id')}

    def as_user(self):
        return self.session.to_user(self._get_parse_dict(), client=self)

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

                await client.update_profile()

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

        await self.session.update_profile(*args, client=self)

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
