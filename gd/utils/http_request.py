import logging
from typing import Sequence

import aiohttp

from .mapper import mapper_util

log = logging.getLogger(__name__)

class HTTPClient:
    """Class that handles the main part of the entire gd.py - sending requests."""
    BASE_URL = "http://www.boomlings.com/database/"

    async def request(self, php, params = None, get_cookies: bool = False, cookie: str = None):
        url = http.BASE_URL + php + ".php"
        method = "GET" if params is None else "POST"
        headers = None
        if cookie is not None:
            headers = {'Cookie': cookie}
        async with aiohttp.ClientSession() as client:
            resp = await client.request(method, url, data=params, headers=headers)
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

    async def fetch(
        self, route: str, parameters: dict = {}, 
        splitter: str = None, error_codes: dict = {},  # error_codes is a dict: {code: error_to_raise}
        raise_errors: bool = True, should_map: bool = False,  # whether response should be mapped 'enum -> value'
        get_cookies: bool = False, cookie: str = None
    ):
        resp = await self.request(route, parameters, get_cookies, cookie)
        if resp in error_codes:
            if raise_errors:
                raise error_codes.get(resp)
            return
        if splitter is not None:
            resp = resp.split(splitter)
        if should_map:
            resp = mapper_util.map(resp)
        return resp

http = HTTPClient()

# TO_DO: rename this to 'http.py'
