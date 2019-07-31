import asyncio

import logging

from .classconverter import ClassConverter
from .errors import *
from .unreguser import UnregisteredUser
from .utils import run as _run
from .utils.captcha_solver import Captcha
from .utils.wrap_tools import _make_repr, check
from .utils.context import ctx
from .utils.http_request import http
from .utils.mapper import mapper_util
from .utils.gdpaginator import paginate
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.indexer import Index as i

log = logging.getLogger(__name__)


class Client:
    """A main class in the gd.py library, used for interacting with the servers of Geometry Dash."""
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
        parameters = Params().create_new().put_definer('song', str(song_id)).finish()
        codes = {
            -1: MissingAccess(type='Song', id=song_id),
            -2: SongRestrictedForUsage(song_id)
        }

        resp = await http.fetch(Route.GET_SONG_INFO, parameters, splitter="~|~", error_codes=codes, should_map=True)
        return ClassConverter.song_convert(resp)
    
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
            Song under given ID was not found or does not exist.

        Returns
        -------
        :class:`.User`
            The user from the ID. (if ID != -1)
        """
        if account_id == -1:
            return UnregisteredUser()

        parameters = Params().create_new().put_definer('user', str(account_id)).finish()
        codes = {
            -1: MissingAccess(type='User', id=account_id)
        }

        resp = await http.fetch(Route.GET_USER_INFO, parameters, splitter=':', error_codes=codes, should_map=True)
        another = Params().create_new().put_definer('search', str(resp.get(i.USER_PLAYER_ID))).put_page(0).finish()
        new_resp = await http.fetch(Route.USER_SEARCH, another, splitter=':', error_codes=codes, should_map=True)

        new_dict = {
            i.USER_GLOW_OUTLINE: new_resp.get(i.USER_GLOW_OUTLINE),
            i.USER_ICON: new_resp.get(i.USER_ICON),
            i.USER_ICON_TYPE: new_resp.get(i.USER_ICON_TYPE)
        }
        for key in list(new_dict.keys()):
            resp[key] = new_dict[key]

        return ClassConverter.user_convert(resp)

    async def test_captcha(self):
        """|coro|

        Tests a Captcha solving, and prints the result.
        """
        resp = await http.request(Route.CAPTCHA)
        res = Captcha().solve(resp, should_log=True)
        print(res)

    def login(self, user: str, password: str):
        """Tries to log in with given parameters.

        .. note::

            This function is not a coroutine, and it is recommended
            to run it before anything asynchronous.

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
        parameters = Params().create_new().put_login_definer(username=user, password=password).finish_login()
        codes = {
            -1: LoginFailure(login=user, password=password)
        }

        resp = _run(
            http.fetch(Route.LOGIN, parameters, splitter=',', error_codes=codes)
        )

        prepared = {
            'name': user, 'password': password,
            'account_id': int(resp[0]), 'id': int(resp[1])
        }
        for attr, value in prepared.items():
            ctx.upd(attr, value)

        log.info("Logged in as %s, with password %s.", repr(user), repr(password))

    @check.is_logged(ctx)
    async def as_user(self):
        return await self.get_user(ctx.account_id)

    @check.is_logged(ctx)
    async def get_page_messages(
        self, sent_or_inbox: str = 'inbox', page: int = 0, *, raise_errors: bool = True
    ):
        assert sent_or_inbox in ('inbox', 'sent')
        inbox = 0 if sent_or_inbox != 'sent' else 1

        params = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_password(ctx.encodedpass).put_page(page).put_total(0).get_sent(inbox).finish()
        codes = {
            -1: MissingAccess(message='Failed to get messages.'),
            -2: NothingFound('gd.Message')
        }

        resp = await http.fetch(
            Route.GET_PRIVATE_MESSAGES, params, error_codes=codes, splitter='#', raise_errors=raise_errors
        )
        if resp is None:
            return []

        to_map = resp[0].split('|')

        res = []
        for elem in to_map:
            mapped = mapper_util.map(elem.split(':'))
            res.append(
                ClassConverter.message_convert(mapped, self._get_parse_dict())
            )

        return res

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
        to_gen = [ctx.name, 0, 0, 1]

        parameters = Params().create_new().put_definer('accountid', str(ctx.account_id)).put_username(ctx.name).put_password(ctx.encodedpass).put_comment(content, to_gen).comment_for('client').finish()
        codes = {
            -1: MissingAccess(message='Failed to post a comment.')
        }

        await http.fetch(Route.UPLOAD_ACC_COMMENT, parameters, error_codes=codes)

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
        _, cookie = await http.request(Route.MANAGE_ACCOUNT, get_cookies=True)
        captcha = await http.request(Route.CAPTCHA, cookie=cookie)
        number = Captcha().solve(captcha)
        params = Params().create_new('web').put_for_management(ctx.name, ctx.password, str(number)).close()
        await http.request(Route.MANAGE_ACCOUNT, params, cookie=cookie)

        if name is not None:
            params = Params().create_new('web').put_for_username(ctx.name, name).close()
            resp = await http.request(Route.CHANGE_USERNAME, params, cookie=cookie)
            if ('Your username has been changed to' in resp):
                log.debug('Changed username to: %s', name)
                ctx.upd('name', name)
            else:
                raise FailedToChange('name')

        if password is not None:
            await http.request(Route.CHANGE_PASSWORD, cookie=cookie)
            params = Params().create_new('web').put_for_password(ctx.name, ctx.password, password).close()
            resp = await http.request(Route.CHANGE_PASSWORD, params, cookie=cookie)
            if ('Password change failed' in resp):
                raise FailedToChange('password')
            else:
                log.debug('Changed password to: %s', password)
                ctx.upd('password', password)

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
