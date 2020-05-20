import asyncio
import platform

from yarl import URL
import aiohttp

import gd

from gd.typing import Any, Dict, List, Optional, Tuple, Type, Union
from gd.logging import get_logger
from gd.errors import HTTPError
from gd.utils.text_tools import make_repr

log = get_logger(__name__)

BASE = "http://www.boomlings.com/database/"
VALID_ERRORS = (OSError, aiohttp.ClientError)


class HTTPClient:
    """Class that handles the main part of the entire gd.py - sending HTTP requests."""

    def __init__(
        self,
        *,
        url: Union[str, URL] = BASE,
        use_user_agent: bool = False,
        forwarded_for: Optional[str] = None,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
        timeout: Union[float, int] = 150,
        max_requests: int = 250,
        debug: bool = False,
        **kwargs,
    ) -> None:
        self.semaphore = asyncio.Semaphore(max_requests)
        self.url = URL(url)
        self.use_agent = use_user_agent
        self.forwarded_for = forwarded_for
        self.proxy = proxy
        self.proxy_auth = proxy_auth
        self.timeout = timeout
        self.debug = debug
        self.last_result = None  # for testing

    def __repr__(self) -> str:
        info = {
            "debug": self.debug,
            "max_requests": self.semaphore._value,
            "timeout": self.timeout,
            "url": repr(self.url),
        }
        return make_repr(self, info)

    @staticmethod
    def get_default_agent() -> str:
        string = "gd.py/{} python/{} aiohttp/{}"
        return string.format(gd.__version__, platform.python_version(), aiohttp.__version__)

    def make_skip_headers(self) -> List[str]:
        return ["User-Agent", "Accept-Encoding"]

    def make_headers(self) -> Dict[str, str]:
        headers = {}

        if self.use_agent:
            headers["User-Agent"] = self.get_default_agent()

        if self.forwarded_for:
            headers["X-Forwarded-For"] = self.forwarded_for

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

    def set_max_requests(
        self, value: int = 250, *, loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        """Creates an :class:`asyncio.Semaphore` object with given ``value`` and ``loop``
        in order to limit amount of max requests at a time.

        Parameters
        ----------
        value: :class:`int`
            Value to set semaphore to. Default is ``250``.
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
        self,
        php: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        get_cookies: bool = False,
        cookie: Optional[str] = None,
        custom_base: Optional[str] = None,
        method: Optional[str] = None,
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
        method: :class:`str`
            Method to use when requesting. This parameter is case insensetive.
            By default, if ``parameters`` is or empty, ``GET`` is used,
            otherwise ``POST`` is used.

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
        url = base / (php + ".php")

        if method is None:
            method = "get" if params is None else "post"

        method = str(method).upper()

        headers = None

        if cookie is not None:
            headers = {"Cookie": cookie}

        if self.debug:
            for name, value in {"URL": url, "Data": data, "Params": params}.items():
                log.debug(f"{name}: {value}")

        async with self.semaphore, aiohttp.ClientSession(
            headers=self.make_headers(),
            skip_auto_headers=self.make_skip_headers(),
            timeout=self.make_timeout(),
            raise_for_status=True,
        ) as client:
            try:
                resp = await client.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    headers=headers,
                    proxy=self.proxy,
                    proxy_auth=self.proxy_auth,
                )
            except VALID_ERRORS as exc:
                raise HTTPError(exc) from None

            data = await resp.content.read()

            if self.debug:
                log.debug(f"Headers: {dict(resp.request_info.headers)!r}")
                self.last_result = data.decode(errors="replace")

                result = self.last_result
                if len(result) > 1000:
                    result = result[:1000] + "..."

                log.debug(f"Response: {result}")

            try:
                res = data.decode()

                try:
                    return int(res)

                except ValueError:
                    pass

            except UnicodeDecodeError:
                res = data

            if get_cookies:
                c = str(resp.cookies).split(" ").pop(1)
                return res, c

            return res

    async def request(
        self,
        route: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        custom_base: Optional[str] = None,
        method: Optional[str] = None,
        # 'error_codes' is a dict: {code: error_to_raise}
        error_codes: Optional[Dict[int, Exception]] = None,
        exclude: Tuple[Type[BaseException]] = (),
        should_map: bool = False,
        get_cookies: bool = False,
        cookie: Optional[str] = None,
    ) -> Optional[Union[bytes, str, int]]:
        """|coro|
        A handy shortcut for fetching response from a server and formatting it.
        Basically does :meth:`HTTPClient.fetch` and operates on its result.

        Parameters
        ----------
        error_codes: Dict[:class:`int`, :exc:`Exception`]
            A dictionary that response is checked against. ``Exception`` can be any Exception.
        exclude: Tuple[Type[:exc:`BaseException`]]
            Types of errors to ignore.

        Raises
        ------
        :exc:`.HTTPError`
            GD Server has destroyed the connection, or machine has no connection.
        :exc:`Exception`
            Exception specified in ``error_codes``, if present.

        Returns
        -------
        Optional[Union[:class:`int`, :class:`bytes`, :class:`str`]]
            If ``error_codes`` is omitted,
            return type is same as return of :meth:`HTTPClient.fetch` call.
            If error is raised and it is in ``exclude``, returns ``None``.
        """
        if params is None:
            params = {}
        if data is None:
            data = {}
        if error_codes is None:
            error_codes = {}

        try:
            resp = await self.fetch(
                php=route,
                data=data,
                params=params,
                get_cookies=get_cookies,
                cookie=cookie,
                custom_base=custom_base,
                method=method,
            )

            if resp in error_codes:
                raise error_codes.get(resp)

        except exclude:
            return

        return resp

    async def normal_request(
        self,
        url: str,
        data: Optional[Union[dict, str]] = None,
        params: Optional[Union[dict, str]] = None,
        method: Optional[str] = None,
        **kwargs,
    ) -> bytes:
        """|coro|
        Same as doing :meth:`aiohttp.ClientSession.request`, where ``method`` is
        either given one or ``"GET"`` if ``data`` is None or omitted, and ``"POST"`` otherwise.
        """
        if method is None:
            method = "GET" if data is None else "POST"
        if data is None:
            data = {}
        if params is None:
            params = {}

        async with aiohttp.ClientSession(timeout=self.make_timeout()) as client:
            try:
                resp = await client.request(
                    method=method, url=url, data=data, params=params, **kwargs
                )
                data = await resp.content.read()

            except VALID_ERRORS as exc:
                raise HTTPError(exc) from None

            if self.debug:
                for name, value in {
                    "URL": url,
                    "Data": data,
                    "Params": params,
                    "Headers": dict(resp.request_info.headers),
                }.items():
                    log.debug(f"{name}: {value}")

        return data


def call_if_possible(some: Any) -> Any:
    if callable(some):
        return some()
    return some
