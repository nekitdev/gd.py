import logging
from typing import Callable, Sequence, Dict

import aiohttp

from ..errors import HTTPNotConnected
from .mapper import mapper_util

log = logging.getLogger(__name__)

class HTTPClient:
    """Class that handles the main part of the entire gd.py - sending HTTP requests."""
    BASE_URL = "http://www.boomlings.com/database/"
    VALID_ERRORS = (
        OSError,
        aiohttp.ClientError
    )

    async def fetch(self, php: str, params: dict = None, get_cookies: bool = False, cookie: str = None):
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

                url = "http://www.boomlings.com/database/" + php + ".php"

        params: Union[:class:`dict`, :class:`str`]
            Parameters to send with the request. Type ``dict`` is prefered.

        get_cookies: :class:`bool`
            Indicates whether to fetch a cookie. This is used
            in different account management actions.

        cookie: :class:`str`
            Cookie, represented as string. Technically should be
            catched with ``get_cookies`` set to ``True``.

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
        url = HTTPClient.BASE_URL + php + ".php"
        method = "GET" if params is None else "POST"
        headers = None
        if cookie is not None:
            headers = {'Cookie': cookie}
        async with aiohttp.ClientSession() as client:
            try:
                resp = await client.request(method, url, data=params, headers=headers)
            except HTTPClient.VALID_ERRORS:
                return
            data = await resp.content.read()
            try:
                res = data.decode()
                if res.replace('-', '').isdigit():  # support for negative integers
                    return int(res)
            except UnicodeDecodeError:
                res = data
            if get_cookies:
                c = str(resp.cookies).split(' ')[1]  # kinda tricky way
                return res, c
            return res

    async def request(
        self, route: str, parameters: dict = {}, 
        splitter: str = None, splitter_func: Callable[[str], list] = None,
        # 'error_codes' is a dict: {code: error_to_raise}
        error_codes: Dict[int, Exception] = {},
        # 'should_map': whether response should be mapped 'enum -> value' (dict)
        raise_errors: bool = True, should_map: bool = False,
        get_cookies: bool = False, cookie: str = None
    ):
        """|coro|

        A handy shortcut for fetching response from a server and formatting it.
        Basically does :meth:`HTTPClient.fetch` and operates on its result.

        Parameters
        ----------
        route: :class:`str`
            Same as ``php`` in :meth:`HTTPClient.fetch`.
        parameters: :class:`dict`
            Same as ``params`` in :meth:`HTTPClient.fetch`
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
        resp = await self.fetch(route, parameters, get_cookies, cookie)

        if resp is None and raise_errors:
            raise HTTPNotConnected()

        assert not (splitter is not None and splitter_func is not None)

        if resp in error_codes:
            if raise_errors:
                raise error_codes.get(resp)
            return

        if not isinstance(resp, int):
            if splitter is not None:
                resp = resp.split(splitter)
            if splitter_func is not None:
                resp = splitter_func(resp)
            if should_map:
                resp = mapper_util.map(resp)
        return resp

    async def normal_request(self, url: str, data = None, **kwargs):
        """|coro|

        Same as doing :meth:`aiohttp.ClientSession.request`, where ``method`` is
        ``"GET"`` if ``data`` is None or omitted, and ``"POST"`` otherwise.
        """
        method = "GET" if data is None else "POST"
        async with aiohttp.ClientSession() as client:
            try:
                resp = await client.request(method, url, data=data, **kwargs)
            except HTTPClient.VALID_ERRORS:
                raise HTTPNotConnected()
            return await resp.content.read()

http = HTTPClient()
