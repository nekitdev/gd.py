import re
import secrets
import types

from iters import iter

from gd.client import Client
from gd.server.common import web
from gd.server.handler import Error, ErrorType
from gd.server.typing import Handler
from gd.text_utils import make_repr
from gd.typing import Any, Callable, Dict, Iterator, Literal, Optional, Type, TypeVar, overload

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

TOKEN_FORMAT = r"[0-9a-zA-Z_]+"

TOKEN_GENERATOR = secrets.token_hex

TOKEN_HEADER = re.compile(fr"(?:Bearer )?(?P<token>{TOKEN_FORMAT})")

TOKEN_LENGTH = 32
TOKEN_LENGTH_SHORT = 8


class Token:
    def __init__(self) -> None:
        self._string = self.generate_string()

    def __repr__(self) -> str:
        info = {"string": self.string}

        return make_repr(self, info)

    def __str__(self) -> str:
        return self.string

    def __hash__(self) -> int:
        return hash(self.string)

    def __eq__(self, other: Any) -> bool:
        return self.string == other

    def __ne__(self, other: Any) -> bool:
        return self.string != other

    @property
    def string(self) -> str:
        return self._string

    @staticmethod
    def generate_string(length: int = TOKEN_LENGTH) -> str:
        return TOKEN_GENERATOR(length)


class ServerToken(Token):
    def __init__(self, name: str, password: str, account_id: int = 0, id: int = 0) -> None:
        super().__init__()

        self._name = name
        self._password = password

        self._account_id = account_id
        self._id = id

    @property
    def name(self) -> str:
        return self._name

    @property
    def password(self) -> str:
        return self._password

    @property
    def account_id(self) -> int:
        return self._account_id

    @property
    def id(self) -> int:
        return self._id

    def is_loaded(self) -> bool:
        return bool(self.name and self.password and self.account_id and self.id)

    async def load(self, client: Client, force: bool = False) -> bool:
        try:
            if self.is_loaded():
                if force:
                    user = await client.get_user(self.account_id, simple=True)

                else:
                    return True

            else:
                user = await client.search_user(self.name, simple=True)

        except Exception:
            return False

        else:
            self._name = user.name
            self._account_id = user.account_id
            self._id = user.id

            return True

    def into(self, client: Client, force: bool = False) -> "ServerTokenContextManager":
        return ServerTokenContextManager(client, self, force=force)


class ServerTokenContextManager:
    def __init__(self, client: Client, token: ServerToken, force: bool = False) -> None:
        self._client = client
        self._token = token
        self._force = force

    @property
    def client(self) -> Client:
        return self._client

    @property
    def token(self) -> ServerToken:
        return self._token

    @property
    def force(self) -> bool:
        return self._force

    async def login(self) -> None:
        client = self.client
        token = self.token

        await token.load(client, force=self.force)

        client.edit(
            name=token.name, password=token.password, account_id=token.account_id, id=token.id
        )

    async def logout(self) -> None:
        await self.client.logout()

    async def __aenter__(self) -> Client:
        await self.login()

        return self.client

    async def __aexit__(
        self, error_type: Type[BaseException], error: BaseException, traceback: types.TracebackType
    ) -> None:
        await self.logout()


TokenT = TypeVar("TokenT", bound="Token")


class TokenDatabase(Dict[str, TokenT]):
    def __init__(self, cls: Type[TokenT] = Token) -> None:  # type: ignore
        self.cls = cls

    def __repr__(self) -> str:
        tokens = ", ".join(self.short_tokens)
        return f"<{self.__class__.__name__} ({tokens})>"

    def copy(self) -> "TokenDatabase[TokenT]":
        cls = self.__class__

        self_copy = cls(self.cls)

        self_copy.update(self)

        return self_copy

    @property
    def short_tokens(self) -> Iterator[str]:
        length = TOKEN_LENGTH_SHORT

        for token in self.plain_tokens:
            yield token[:length]

    @property
    def plain_tokens(self) -> Iterator[str]:
        yield from self.keys()

    @property
    def tokens(self) -> Iterator[TokenT]:
        yield from self.values()

    def contains(self, token: str) -> bool:
        return token in self

    def insert(self, token: TokenT) -> TokenT:
        self[token.string] = token

        return token

    def remove(self, token: str) -> None:
        try:
            del self[token]

        except KeyError:
            pass


class ServerTokenDatabase(TokenDatabase[ServerToken]):
    def __init__(self, cls: Type[ServerToken] = ServerToken) -> None:
        super().__init__(ServerToken)

    def get_user(self, name: str, password: str) -> Optional[ServerToken]:
        return iter(self.tokens).get(name=name, password=password)

    def register(
        self, name: str, password: str, account_id: int = 0, id: int = 0
    ) -> ServerToken:
        return super().insert(
            self.cls(name=name, password=password, account_id=account_id, id=id)
        )


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
