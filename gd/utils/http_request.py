import asyncio
import platform
import random

from yarl import URL
import aiohttp

import gd

from ..typing import Dict, Optional, Union
from ..logging import get_logger
from ..errors import HTTPError
from .text_tools import make_repr

log = get_logger(__name__)

BASE = 'http://www.boomlings.com/database/'
VALID_ERRORS = (
    OSError,
    aiohttp.ClientError
)


class HTTPClient:
    """Class that handles the main part of the entire gd.py - sending HTTP requests."""
    def __init__(
        self, *, url: Union[str, URL] = BASE,
        timeout: Union[float, int] = 150,
        debug: bool = False, ip: str = 'default',
        user_agent: Optional[str] = None,
        use_user_agent: bool = True,
        semaphore: Optional[asyncio.Semaphore] = None
    ) -> None:
        if semaphore is None:
            semaphore = asyncio.Semaphore(250)

        if user_agent is None:
            user_agent = self.get_default_agent()

        self.user_agent = user_agent
        self.use_user_agent = use_user_agent
        self.url = URL(url)
        self.ip = ip
        self.semaphore = semaphore
        self.timeout = timeout
        self.debug = debug
        self.last_result = None  # for testing

    def __repr__(self) -> str:
        info = {
            'debug': self.debug,
            'ip': self.ip,
            'max_requests': self.semaphore._value,
            'timeout': self.timeout,
            'url': repr(self.url),
            'user_agent': repr(self.user_agent)
        }
        return make_repr(self, info)

    @staticmethod
    def get_default_agent() -> str:
        string = 'GDClient (gd.py {}) Python/{} aiohttp/{}'
        return string.format(gd.__version__, platform.python_version(), aiohttp.__version__)

    @staticmethod
    def make_random_ipv4() -> str:
        return ('.').join(map(str, (random.randint(0, 255) for _ in range(4))))

    def make_headers(self) -> Dict[str, str]:
        headers = {}

        if self.use_user_agent:
            headers['User-Agent'] = self.user_agent

        if self.ip != 'default':
            headers['X-Forwarded-For'] = (
                self.ip if self.ip != 'random' else self.make_random_ipv4()
            )

        return headers

    def make_timeout(self) -> aiohttp.ClientTimeout:
        return aiohttp.ClientTimeout(total=self.timeout)

    def change_url(self, url: Union[str, URL]) -> None:
        """Change base for requests.

        Default base is ``http://www.boomlings.com/database/``,
        but it can be changed.

        Parameters
        ----------
        url: :class:`str`
            Base to change HTTPClient base to.
        """
        self.url = URL(url)

    def set_semaphore(
        self, value: int = 250, *,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:
        """Sets semaphore to :class:`asyncio.Semaphore` with given value and loop.

        Parameters
        ----------
        value: :class:`int`
            Value to set semaphore to. Default is ``200``.

        loop: :class:`asyncio.AbstractEventLoop`
            Event loop to pass to semaphore's constructor.
        """
        self.semaphore = asyncio.Semaphore(value, loop=loop)

    def set_debug(self, debug: bool = False) -> None:
        """Set http client debugging.

        Parameters
        ----------
        debug: :class:`bool`
            Whether to set debug on or off.
        """
        self.debug = bool(debug)

    async def fetch(
        self, php: str, params: Optional[Union[dict, str]] = None, get_cookies: bool = False,
        cookie: Optional[str] = None, custom_base: Optional[str] = None
    ) -> Optional[Union[bytes, int, str]]:
        """|coro|

        Sends an HTTP Request to a Geometry Dash server and returns the response.

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

        custom_base: [:class:`str`, :class:`yarl.URL`]
            Custom base using different Geometry Dash IP.
            By default ``self.base`` is used.

        Returns
        -------
        Union[:class:`bytes`, :class:`str`, :class:`int`]
            ``res`` with the following rules:

            Returns an :class:`int`, representing server error code, e.g. ``-1``,
            if server responded with error.

            Otherwise, returns response from a server as a :class:`str` if successfully
            decodes it, and on fail returns :class:`bytes`.

            If a cookie is requested, returns a pair (``res``, ``c``) where c is a :class:`str` cookie.

        Raises
        ------
        :exc:`.HTTPError`
            An exception occured during handling request/response.
        """
        base = self.url if custom_base is None else URL(custom_base)
        url = base / (php + '.php')

        method = 'GET' if params is None else 'POST'
        headers = None

        if cookie is not None:
            headers = {'Cookie': cookie}

        skip = []

        if not self.use_user_agent:
            skip.append('User-Agent')

        if self.debug:
            log.debug('URL: {}'.format(url))
            log.debug('Data: {}'.format(params))

        async with self.semaphore, aiohttp.ClientSession(
            headers=self.make_headers(),
            skip_auto_headers=skip,
            timeout=self.make_timeout()
        ) as client:
            try:
                resp = await client.request(method, url, data=params, headers=headers)
            except VALID_ERRORS as exc:
                raise HTTPError(exc) from None

            data = await resp.content.read()

            if self.debug:
                log.debug('Headers: {!r}'.format(resp.request_info.headers))
                self.last_result = data.decode(errors='replace')
                log.debug('Response: {!r}'.format(self.last_result))

            try:
                res = data.decode()

                try:
                    return int(res)

                except ValueError:
                    pass

            except UnicodeDecodeError:
                res = data

            if get_cookies:
                c = str(resp.cookies).split(' ').pop(1)
                return res, c

            return res

    async def request(
        self, route: str, parameters: Optional[Union[dict, str]] = None,
        custom_base: Optional[str] = None,
        # 'error_codes' is a dict: {code: error_to_raise}
        error_codes: Optional[Dict[int, Exception]] = None,
        raise_errors: bool = True, should_map: bool = False,
        get_cookies: bool = False, cookie: Optional[str] = None
    ) -> Optional[Union[bytes, str, int]]:
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
        error_codes: Dict[:class:`int`, :exc:`Exception`]
            A dictionary that response is checked against. ``Exception`` can be any Exception.
        raise_errors: :class:`bool`
            If ``False``, errors are not raised.
            (technically, just turns on ignoring ``error_codes``)
        get_cookies: :class:`bool`
            Same as ``get_cookies`` in :meth:`HTTPClient.fetch`
        cookie: :class:`str`
            Same as ``cookie`` in :meth:`HTTPClient.fetch`

        Raises
        ------
        :exc:`.HTTPError`
            GD Server has destroyed the connection, or machine has no connection.
            Raised when :meth:`HTTPClient.fetch` returns ``None`` and ``raise_errors`` is ``True``.

        :exc:`Exception`
            Exception specified in ``error_codes``, if present.

        Returns
        -------
        Optional[Union[:class:`int`, :class:`bytes`, :class:`str`]]
            If ``error_codes`` is omitted,
            return type is same as return of :meth:`HTTPClient.fetch` call.

            If ``error_codes`` is specified, and ``raise_errors`` is ``False``, returns ``None``
            when response is in ``error_codes``.
        """
        if parameters is None:
            parameters = {}

        if error_codes is None:
            error_codes = {}

        try:
            resp = await self.fetch(route, parameters, get_cookies, cookie, custom_base)
        except HTTPError:
            if raise_errors:
                raise
            return

        if resp in error_codes:
            if raise_errors:
                raise error_codes.get(resp)
            return

        return resp

    async def normal_request(
        self, url: str, data: Optional[Union[dict, str]] = None,
        params: Optional[Union[dict, str]] = None,
        method: Optional[str] = None, **kwargs
    ) -> aiohttp.ClientResponse:
        """|coro|

        Same as doing :meth:`aiohttp.ClientSession.request`, where ``method`` is
        either given one or ``"GET"`` if ``data`` is None or omitted, and ``"POST"`` otherwise.
        """
        if method is None:
            method = 'GET' if data is None else 'POST'

        if data is None:
            data = {}

        if params is None:
            params = {}

        async with aiohttp.ClientSession(headers=self.make_headers(), timeout=self.make_timeout()) as client:
            try:
                resp = await client.request(method, url, data=data, params=params, **kwargs)

            except VALID_ERRORS as exc:
                raise HTTPError(exc) from None

            if self.debug:
                for name, value in zip(
                    ('URL', 'Data', 'Params', 'Headers'),
                    (url, data, params, resp.request_info.headers)
                ):
                    log.debug('{}: {}'.format(name, value))

        return resp
