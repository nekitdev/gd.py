from __future__ import annotations

from secrets import token_hex
from types import TracebackType as Traceback
from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar, overload
import re

from attrs import field, frozen
from iters import iter
from typing_extensions import Literal

from gd.credentials import Credentials
from gd.server.common import web
from gd.server.handler import Error, ErrorType
from gd.server.typing import Handler
from gd.typing import AnyException, StringDict

if TYPE_CHECKING:
    from gd.client import Client

__all__ = (
    "ServerToken",
    "ServerTokenContextManager",
    "ServerTokenDatabase",
    "Token",
    "TokenDatabase",
    "get_token_from_request",
    "token",
)

AUTHORIZATION = "Authorization"

TOKEN_PATTERN = r"[0-9a-zA-Z_]+"

TOKEN_HEADER = re.compile(rf"(?:Bearer )?(?P<token>{TOKEN_FORMAT})")

TOKEN_LENGTH = 32
TOKEN_SHORT_LENGTH = 8


@frozen()
class Token:
    string: str = field()

    @string.default
    def default_string(self) -> str:
        return self.generate_string()

    @property
    def short_string(self, short_length: int = TOKEN_SHORT_LENGTH) -> str:
        return self.string[:short_length]

    @staticmethod
    def generate_string(length: int = TOKEN_LENGTH) -> str:
        return token_hex(length)

    def __str__(self) -> str:
        return self.string

    def __hash__(self) -> int:
        return hash(self.string)


C = TypeVar("C", bound="Client")

ST = TypeVar("ST", bound="ServerToken")


class ServerToken(Token):
    credentials: Credentials = field(factory=Credentials)

    def is_loaded(self) -> bool:
        return self.credentials.is_loaded()

    @property
    def account_id(self) -> int:
        return self.credentials.account_id

    @property
    def id(self) -> int:
        return self.credentials.id

    @property
    def name(self) -> str:
        return self.credentials.name

    @property
    def password(self) -> str:
        return self.credentials.password

    def into(self: ST, client: C) -> ServerTokenContextManager[ST, C]:
        return ServerTokenContextManager(self, client)

    async def login(self, client: Client) -> None:
        await self.client.login(self.name, self.password)

        self.credentials = client.credentials

    async def logout(self, client: Client) -> None:
        await client.logout()


E = TypeVar("E", bound=AnyException)


@frozen()
class ServerTokenContextManager(Generic[ST, C]):
    token: ST
    client: C

    async def login(self) -> None:
        await self.token.login(self.client)

    async def logout(self) -> None:
        await self.token.logout(self.client)

    async def __aenter__(self) -> C:
        await self.login()

        return self.client

    @overload
    async def __aexit__(self, error_type: None, error: None, traceback: None) -> None:
        ...

    @overload
    async def __aexit__(self, error_type: Type[E], error: E, traceback: Traceback) -> None:
        ...

    async def __aexit__(
        self, error_type: Optional[Type[E]], error: Optional[E], traceback: Optional[Traceback]
    ) -> None:
        await self.logout()


T = TypeVar("T", bound="Token")

TD = TypeVar("TD", bound="TokenDatabase[Token]")


class TokenDatabase(StringDict[T]):
    def copy(self: TD) -> TD:
        copy = type(self)(self.token_type)

        copy.update(self)

        return copy

    def contains(self, token: str) -> bool:
        return token in self

    def insert(self, token: T) -> T:
        self[token.string] = token

        return token

    def remove(self, token: str) -> None:
        if token in self:
            del self[token]


class ServerTokenDatabase(TokenDatabase[ServerToken]):
    def get_user(self, name: str, password: str) -> Optional[ServerToken]:
        return iter(self.tokens).get_or_none(name=name, password=password)

    def register(self, name: str, password: str, account_id: int = 0, id: int = 0) -> ServerToken:
        return super().insert(self.cls(name=name, password=password, account_id=account_id, id=id))


@overload  # noqa
def get_token_from_request(request: web.Request, required: Literal[True]) -> Token:  # noqa
    ...


@overload  # noqa
def get_token_from_request(  # noqa
    request: web.Request, required: Literal[False]
) -> Optional[Token]:
    ...


@overload  # noqa
def get_token_from_request(request: web.Request, required: bool) -> Optional[Token]:  # noqa
    ...


def get_token_from_request(request: web.Request, required: bool = False) -> Optional[Token]:  # noqa
    token_database = request.app.token_database  # type: ignore

    header = request.headers.get(AUTHORIZATION)

    if header is None:
        string = request.query.get("token")

        if string is None:
            if required:
                raise TypeError("Can not find token in the request.")

            return None

    else:
        match = TOKEN_HEADER.fullmatch(header)

        if match is None:
            if required:
                raise ValueError("Provided token is invalid.")

            return None

        else:
            string = match.group("token")

    token = token_database.get(string)

    if token is None:
        if required:
            raise LookupError("Token was not found in the database.")

        return None

    else:
        return token


def token(required: bool = False) -> Callable[[Handler], Handler]:
    def wrapper(handler: Handler) -> Handler:
        async def handler_with_token(request: web.Request) -> web.StreamResponse:
            try:
                token = get_token_from_request(request, required=required)

            except ValueError:
                return Error(401, ErrorType.AUTH_INVALID, "Token is invalid.").into_response()

            except LookupError:
                return Error(
                    401, ErrorType.AUTH_MISSING, "Token is not present in the database."
                ).into_response()

            except TypeError:
                return Error(
                    401, ErrorType.AUTH_NOT_SET, "Token is not set in the request."
                ).into_response()

            else:
                request.token = token

                return await handler(request)

        return handler_with_token

    return wrapper
