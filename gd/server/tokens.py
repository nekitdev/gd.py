from __future__ import annotations

import re
from secrets import token_hex
from types import TracebackType as Traceback
from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar, overload

from aiohttp.web import Request, StreamResponse
from attrs import field, frozen
from typing_extensions import Literal

from gd.credentials import Credentials
from gd.server.constants import AUTHORIZATION, HTTP_UNAUTHORIZED, TOKEN, TOKENS
from gd.server.handler import Error, ErrorType
from gd.server.typing import StreamHandler
from gd.typing import AnyException, DecoratorIdentity, Predicate, StringDict

if TYPE_CHECKING:
    from gd.client import Client

__all__ = (
    "ServerToken",
    "ServerTokenContextManager",
    "ServerTokens",
    "Token",
    "Tokens",
    "get_token_from_request",
    "token",
)

TOKEN_PATTERN = r"[0-9a-zA-Z_]+"

TOKEN_HEADER = re.compile(rf"(?:Bearer )?(?P<token>{TOKEN_PATTERN})")

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


@frozen()
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

    def apply(self: ST, client: C) -> ServerTokenContextManager[ST, C]:
        return ServerTokenContextManager(self, client)

    async def login(self, client: Client) -> None:
        await self.client.login(self.name, self.password)

        self.credentials = client.credentials

    async def logout(self, client: Client) -> None:
        await client.logout()

        self.credentials = client.credentials


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

Ts = TypeVar("Ts", bound="AnyTokens")


class Tokens(StringDict[T]):
    def __init__(self, token_type: Type[T]) -> None:
        self._token_type = token_type

    @property
    def token_type(self) -> Type[T]:
        return self._token_type

    def copy(self: Ts) -> Ts:
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


AnyTokens = Tokens[Token]


def by_name_and_password(name: str, password: str) -> Predicate[ServerToken]:
    def predicate(token: ServerToken) -> bool:
        return token.name == name and token.password == password

    return predicate


ST = TypeVar("ST", bound=ServerToken)


class ServerTokens(Tokens[ST]):
    def get_user(self, name: str, password: str) -> Optional[ST]:
        return next(filter(by_name_and_password(name, password), self.values()), None)

    def register(
        self,
        name: str,
        password: str,
        account_id: int = 0,
        id: int = 0,
        credentials_type: Type[Credentials] = Credentials,
    ) -> ServerToken:
        return self.insert(
            self.token_type(
                credentials=credentials_type(
                    name=name, password=password, account_id=account_id, id=id
                )
            )
        )


CAN_NOT_FIND_TOKEN = "can not find the token in the request"
INVALID_TOKEN = "provided token is invalid"
TOKEN_NOT_FOUND = "the token was not found in the database"


@overload
def get_token_from_request(request: Request, required: Literal[True]) -> Token:
    ...


@overload
def get_token_from_request(request: Request, required: Literal[False]) -> Optional[Token]:
    ...


@overload
def get_token_from_request(request: Request, required: bool) -> Optional[Token]:
    ...


def get_token_from_request(request: Request, required: bool = False) -> Optional[Token]:
    tokens = request.app[TOKENS]

    header = request.headers.get(AUTHORIZATION)

    if header is None:
        string = request.query.get(TOKEN)

        if string is None:
            if required:
                raise TypeError(CAN_NOT_FIND_TOKEN)

            return None

    else:
        match = TOKEN_HEADER.fullmatch(header)

        if match is None:
            if required:
                raise ValueError(INVALID_TOKEN)

            return None

        else:
            string = match.group(TOKEN)

    token = tokens.get(string)

    if token is None:
        if required:
            raise LookupError(TOKEN_NOT_FOUND)

        return None

    else:
        return token


INVALID_TOKEN_MESSAGE = "the token is invalid"
TOKEN_NOT_FOUND_MESSAGE = "the token is not present in the database"
CAN_NOT_FIND_TOKEN_MESSAGE = "can not find the token in the request"


def token(required: bool = False) -> DecoratorIdentity[StreamHandler]:
    def wrapper(handler: StreamHandler) -> StreamHandler:
        async def handler_with_token(request: Request) -> StreamResponse:
            try:
                token = get_token_from_request(request, required=required)

            except ValueError:
                return Error(
                    HTTP_UNAUTHORIZED, ErrorType.AUTH_INVALID, INVALID_TOKEN_MESSAGE
                ).into_response()

            except LookupError:
                return Error(
                    HTTP_UNAUTHORIZED, ErrorType.AUTH_MISSING, TOKEN_NOT_FOUND_MESSAGE
                ).into_response()

            except TypeError:
                return Error(
                    HTTP_UNAUTHORIZED, ErrorType.AUTH_NOT_SET, CAN_NOT_FIND_TOKEN_MESSAGE
                ).into_response()

            else:
                request[TOKEN] = token

                return await handler(request)

        return handler_with_token

    return wrapper
