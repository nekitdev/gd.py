import asyncio

import logging
from typing import Sequence, Union

from .session import GDSession

from .utils.wrap_tools import _make_repr, check
from .utils.context import ctx

log = logging.getLogger(__name__)

# The theme for debates: should ctx be used or gd.Client passed on object __init__ instead?
# Your opinion in /issues section!

class Client:
    """A main class in the gd.py library, used for interacting with the servers of Geometry Dash."""
    def __init__(self):
        self.session = GDSession()

    def __repr__(self):
        info = {
            'is_logged': ctx.is_logged()
        }
        return _make_repr(self, info)

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
        return await self.session.get_user(account_id)

    async def search_user(self, query: Union[int, str] = None):
        """|coro|

        Searches for a user on Geometry Dash servers.

        Raises
        ------
        :exc:`.MissingAccess`
            Nothing was found.

        Returns
        -------
        :class:`.AbstractUser`
            An AbstractUser found when searching with the query.
        """
        return await self.session.search_user(query)

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
        return await self.session.get_timely('daily')

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
        return await self.session.get_timely('weekly')

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
                Use :meth:`.Client.get_timely` instead.

        Raises
        ------
        :exc:`.MissingAccess`
            Level with given ID was not found.

        Returns
        -------
        :class:`.Level`
            The level corresponding to given id.
        """
        return await self.session.get_level(level_id)

    async def test_captcha(self):
        """|coro|

        Tests Captcha solving, and prints the result.
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
        await self.session.login(user=user, password=password)
        log.info("Logged in as %s, with password %s.", repr(user), repr(password))

    @check.is_logged(ctx)
    async def as_user(self):
        """|coro|

        Gets user with ``account_id`` defined in context,
        which means that client should be logged in.

        Returns
        -------
        :class:`.User`
            User corresponding to ``ctx.account_id``
        """
        return await self.get_user(ctx.account_id)

    @check.is_logged(ctx)
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
            raise_errors=raise_errors, udict=self._gen_parse_dict()
        )

    @check.is_logged(ctx)
    def _get_parse_dict(self):
        return {k: getattr(ctx, k) for k in ('name', 'id', 'account_id')}

    @check.is_logged(ctx)
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
        await self.session.post_comment(content)

        log.debug("Posted a comment. Content: %s", content)

    @check.is_logged(ctx)
    async def edit(self, name = None, password = None):
        """|coro|

        Tries to edit credentials of a client, if logged in.

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
        await self.session.edit(name=name, password=password)

        # if no errors occured, log changes.
        if name is not None:
            log.debug('Changed username to: %s', name)

        if password is not None:
            log.debug('Changed password to: %s', password)

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
