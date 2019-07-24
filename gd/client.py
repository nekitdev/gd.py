import asyncio

import logging

from .utils.captcha_solver import Captcha
from .utils.wrap_tools import _make_repr, check
from .utils.context import ctx
from .utils.http_request import http
from .classconverter import class_converter
from .utils.mapper import mapper_util
from .errors import *
from .utils.gdpaginator import paginate
from .utils.routes import Route
from .utils.params import Parameters as Params
from .utils.indexer import Index as i
from .unreguser import UnregisteredUser
from .authclient import AuthClient

log = logging.getLogger(__name__)


class Client:
    """A main class in the gd.py library, used for interacting with the servers of Geometry Dash."""
    def __repr__(self):
        info = {
            'is_logged': ctx.is_logged()
        }
        return _make_repr(self, info)

    async def get_song(self, songid: int = 0):
        """|coro|

        Fetches a song from Geometry Dash server.

        Parameters
        ----------
        songid: :class:`int`
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
        parameters = Params().create_new().put_definer('song', str(songid)).finish()
        codes = {
            -1: MissingAccess(type='Song', id=songid),
            -2: SongRestrictedForUsage(songid)
        }
        resp = await http.fetch(Route.GET_SONG_INFO, parameters, splitter="~|~", error_codes=codes, should_map=True)
        return class_converter.SongConvert(resp)
    
    async def get_user(self, accountid: int = 0):
        """|coro|

        Fetches a user from Geometry Dash server.

        Parameters
        ----------
        accountid: :class:`int`
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
        if accountid == -1:
            return UnregisteredUser()
        parameters = Params().create_new().put_definer('user', str(accountid)).finish()
        codes = {
            -1: MissingAccess(type='User', id=accountid)
        }
        resp = await http.fetch(Route.GET_USER_INFO, parameters, splitter=':', error_codes=codes, should_map=True)

        another = Params().create_new().put_definer('search', str(mapped.get(i.USER_PLAYER_ID))).put_page(0).finish()
        new_resp = http.send_request(Route.USER_SEARCH, another, splitter=':', error_codes=codes, should_map=True)
        new_dict = {
            i.USER_GLOW_OUTLINE: new_resp.get(i.USER_GLOW_OUTLINE),
            i.USER_ICON: new_resp.get(i.USER_ICON),
            i.USER_ICON_TYPE: new_resp.get(i.USER_ICON_TYPE)
        }
        for key in list(new_dict.keys()):
            mapped[key] = new_dict[key]
        return class_converter.UserConvert(mapped)
    
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
        loop = asyncio.new_event_loop()
        resp = loop.run_until_complete(
            http.fetch(Route.LOGIN, parameters, splitter=',', error_codes=codes)
        )
        loop.close()
        prepared = {
            'name': user, 'password': password,
            'account_id': int(resp[0]), 'id': int(resp[1])
        }
        for attr, value in prepared.items():
            ctx.upd(attr, value)
        log.info("Logged in as %s, with password %s", repr(user), repr(password))

    @check.is_logged(ctx)
    async def edit(self, name = None, password = None):
        """|coro|

        Tries to edit credentials of a logged in client.

        Parameters
        ----------
        name: :class:`str`
            A name to change logged account's username to. Defaults to `None`.

        password: :class:`str`
            A password to change logged account's username to. Defaults to `None`.

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
        """A decorator that registers an event to listen to."""

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function.")

        setattr(self, coro.__name__, coro)
        log.debug("%s has been successfully registered as an event.", coro.__name__)

        return coro
