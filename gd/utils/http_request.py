import asyncio
import logging
from typing import Callable, Dict

import aiohttp

from ..errors import HTTPNotConnected
from .mapper import mapper_util
from .wrap_tools import make_repr

log = logging.getLogger(__name__)

class HTTPClient:
    """Class that handles the main part of the entire gd.py - sending HTTP requests.

    Attributes
    ----------
    semaphore: Optional[:class:`asyncio.Semaphore`]
        A semaphore to use when doing requests. Defaults to :class:`asyncio.Semaphore` with value ``200``.
    """
    BASE = 'http://www.boomlings.com/database/'
    VALID_ERRORS = (
        OSError,
        aiohttp.ClientError
    )

    def __init__(self, *, semaphore=None):
        self.semaphore = semaphore or asyncio.Semaphore(250)
        self.debug = False
        self._last_result = None  # for testing purposes

    def __repr__(self):
        info = {
            'debug': self.debug,
            'semaphore': self.semaphore,
            'url': HTTPClient.BASE
        }
        return make_repr(self, info)

    @classmethod
    def change_base(cls, base: str = None):
        """Change base for requests.

        Default base is ``http://www.boomlings.com/database/``,
        but it can be changed.

        Parameters
        ----------
        base: :class:`str`
            Base to change HTTPClient base to. If ``None`` or omitted, current base is preserved.
        """
        if base is None:
            return
        cls.BASE = base

    def set_default_semaphore(self, value: int = 250, *, loop=None):
        """Sets semaphore to :class:`asyncio.Semaphore` with given value and loop.

        Parameters
        ----------
        value: :class:`int`
            Value to set semaphore to. Default is ``200``.

        loop: :class:`asyncio.AbstractEventLoop`
            Event loop to pass to semaphore's constructor.
        """
        self.semaphore = asyncio.Semaphore(value, loop=loop)

    def set_semaphore(self, semaphore):
        """Sets semaphore of ``self`` to a given ``semaphore``.

        Parameters
        ----------
        semaphore: `Any`
            Semaphore to set. Preferably from ``asyncio`` module or subclasses of asyncio semaphores.
        """
        self.semaphore = semaphore

    def set_debug(self, debug: bool = False):
        """Set http client debugging.

        Parameters
        ----------
        debug: :class:`bool`
            Whether to set debug on or off.
        """
        self.debug = bool(debug)

    async def fetch(
        self, php: str, params: dict = None, get_cookies: bool = False,
        cookie: str = None, custom_base: str = None, run_decoding: bool = True
    ):
        """|coro|

        Sends an HTTP Request to a Geometry Dash server and returns the response.

        .. note::
            This method does not raise any errors, but still,
            should be used carefully in programs.

        Parameters
        ----------
        php: :class:`str`
            The endpoint for the request URL, passed like this:

            .. code-block:: python3

                url = 'http://www.boomlings.com/database/' + php + '.php'

        params: Union[:class:`dict`, :class:`str`]
            Parameters to send with the request. Type ``dict`` is prefered.

        get_cookies: :class:`bool`
            Indicates whether to fetch a cookie. This is used
            in different account management actions.

        cookie: :class:`str`
            Cookie, represented as string. Technically should be
            catched with ``get_cookies`` set to ``True``.

        custom_base: :class:`str`
            Custom base using different Geometry Dash IP.
            By default ``http://boomlings.com/database/`` is used.

        run_decoding: :class:`bool`
            Indicates whether to decode recieved response text.

        Returns
        -------
        Union[:class:`bytes`, :class:`str`, :class:`int`, `None`]
            ``res`` with the following rules:

            If Exception occurs while sending request, returns ``None``.

            Returns an :class:`int`, representing server error code, e.g. ``-1``,
            if server responded with error.

            Otherwise, returns response from a server as a :class:`str` if successfully
            decodes it, and on fail returns :class:`bytes`.

            If a cookie is requested, returns a pair (``res``, ``c``) where c is a :class:`str` cookie.
        """
        base = HTTPClient.BASE if custom_base is None else custom_base
        url = base + php + '.php'

        method = 'GET' if params is None else 'POST'
        headers = None

        if cookie is not None:
            headers = {'Cookie': cookie}

        if self.debug:
            print('URL: {}, Data: {}'.format(url, params))

        async with aiohttp.ClientSession() as client:
            async with self.semaphore:
                try:
                    resp = await client.request(method, url, data=params, headers=headers)
                except HTTPClient.VALID_ERRORS:
                    return

                data = await resp.content.read()
                self._last_result = data

                try:
                    if run_decoding:
                        res = data.decode()

                        try:
                            return int(res)
                        except ValueError:
                            pass

                    else:
                        res = data

                except UnicodeDecodeError:
                    res = data

                if self.debug:
                    print(res)

                if get_cookies:
                    c = str(resp.cookies).split(' ')[1]
                    return res, c

                return res

    async def request(
        self, route: str, parameters: dict = None, custom_base: str = None,
        splitter: str = None, splitter_func: Callable[[str], list] = None,
        # 'error_codes' is a dict: {code: error_to_raise}
        error_codes: Dict[int, Exception] = None,
        # 'should_map': whether response should be mapped 'enum -> value' (dict)
        raise_errors: bool = True, should_map: bool = False,
        get_cookies: bool = False, cookie: str = None, run_decoding: bool = True
    ):
        """|coro|

        A handy shortcut for fetching response from a server and formatting it.
        Basically does :meth:`HTTPClient.fetch` and operates on its result.

        Parameters
        ----------
        route: :class:`str`
            Same as ``php`` in :meth:`HTTPClient.fetch`.
        parameters: :class:`dict`
            Same as ``params`` in :meth:`HTTPClient.fetch`.
        custom_base: :class:`str`
            Same as ``custom_base`` in :meth:`HTTPClient.fetch`.
        splitter: :class:`str`
            A string to split the response with. If ``None``, splitting is passed.
        splitter_func: Callable[[:class:`str`], :class:`list`]
            A function that takes one argument of type string. Preferably should return a list.

            .. note::

                Either *splitter* can be specified, or *splitter_func*. Not both.

        error_codes: Dict[:class:`int`, :exc:`Exception`]
            A dictionary that response is checked against. ``Exception`` can be any Exception.
        raise_errors: :class:`bool`
            If ``False``, errors are not raised.
            (technically, just turns on ignoring ``error_codes``)
        should_map: :class:`bool`
            Whether should operate :meth:`.mapper_util.map` or not,
            considering that current response is converted to a list.
        get_cookies: :class:`bool`
            Same as ``get_cookies`` in :meth:`HTTPClient.fetch`
        cookie: :class:`str`
            Same as ``cookie`` in :meth:`HTTPClient.fetch`
        run_decoding: :class:`bool`
            Same as ``run_decoding`` in :meth:`HTTPClient.fetch`

        Raises
        ------
        :exc:`.HTTPNotConnected`
            GD Server has destroyed the connection, or machine has no connection.
            Raised when :meth:`HTTPClient.fetch` returns ``None`` and ``raise_errors`` is ``True``.

        :exc:`Exception`
            Exception specified in ``error_codes``, if present.

        Returns
        -------
        Union[:class:`int`, :class:`bytes`, :class:`str`, :class:`list`, :class:`dict`, `None`]
            If ``splitter``, ``splitter_func``, ``should_map`` and ``error_codes`` are omitted,
            return type is same as return of :meth:`HTTPClient.fetch` call.

            If ``error_codes`` is specified, and ``raise_errors`` is ``False``, returns ``None``
            when response is in ``error_codes``.

            If ``splitter`` is not ``None``, and ``should_map`` is
            ``False`` or omitted, returns :class:`list`.

            If ``splitter_func`` is not ``None`` and ``should_map`` is not present or ``False``,
            returns whatever passed function does return.

            If ``should_map`` is ``True``, returns :class:`dict`.
        """
        if parameters is None:
            parameters = {}

        if error_codes is None:
            error_codes = {}

        resp = await self.fetch(route, parameters, get_cookies, cookie, custom_base, run_decoding)

        if resp is None:
            if raise_errors:
                raise HTTPNotConnected()
            return

        if resp in error_codes:
            if raise_errors:
                raise error_codes.get(resp)
            return

        assert not (splitter is not None and splitter_func is not None)

        if not isinstance(resp, int):
            if splitter is not None:
                resp = resp.split(splitter)
            if splitter_func is not None:
                resp = splitter_func(resp)
            if should_map:
                resp = mapper_util.map(resp)
        return resp

    async def normal_request(self, url: str, data = None, method: str = None, **kwargs):
        """|coro|

        Same as doing :meth:`aiohttp.ClientSession.request`, where ``method`` is
        either given one or ``"GET"`` if ``data`` is None or omitted, and ``"POST"`` otherwise.
        """
        if method is None:
            method = 'GET' if data is None else 'POST'

        async with aiohttp.ClientSession() as client:
            try:
                resp = await client.request(method, url, data=data, **kwargs)

            except HTTPClient.VALID_ERRORS:
                raise HTTPNotConnected()

        return resp

http = HTTPClient()
