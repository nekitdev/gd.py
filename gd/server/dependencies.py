import re
from typing import Iterable, Optional

from fastapi import Request

from gd.constants import DEFAULT_PAGES
from gd.errors import InternalError
from gd.server.core import tokens
from gd.server.errors import AuthenticationInvalid, AuthenticationMissing, AuthenticationNotFound
from gd.server.tokens import ServerToken
from gd.server.utils import parse_pages

__all__ = ("pages_dependency", "token_dependency")


def pages_dependency(pages: Optional[str] = None) -> Iterable[int]:
    if pages is None:
        return DEFAULT_PAGES

    return parse_pages(pages)


HEX = r"[0-9a-f]"
TOKEN = "token"
BEARER_PATTERN = rf"Bearer (?P<{TOKEN}>{HEX}+)"
BEARER = re.compile(BEARER_PATTERN)

AUTHORIZATION = "Authorization"


def token_dependency(request: Request, token: Optional[str] = None) -> ServerToken:
    if token is None:
        header = request.headers.get(AUTHORIZATION)

        if header is None:
            raise AuthenticationMissing()

        match = BEARER.match(header)

        if match is None:
            raise AuthenticationInvalid()

        token = match.group(TOKEN)

        if token is None:
            raise InternalError  # TODO: message?

    result = tokens.get(token)

    if result is None:
        raise AuthenticationNotFound()

    return result
