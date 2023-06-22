from secrets import token_hex as standard_generate_token
from typing import Any, Optional, Type, TypeVar

from attrs import field, frozen
from iters.iters import iter
from typing_aliases import Predicate, StringDict
from typing_extensions import TypedDict

from gd.client import Client
from gd.server.constants import DEFAULT_SIZE

__all__ = ("ServerToken", "ServerTokens", "Token", "TokenData", "Tokens")


class TokenData(TypedDict):
    token: str


def generate_token(size: int = DEFAULT_SIZE) -> str:
    return standard_generate_token(size)


T = TypeVar("T", bound="Token")


@frozen()
class Token:
    value: str = field(factory=generate_token)

    def __str__(self) -> str:
        return self.value


ST = TypeVar("ST", bound="ServerToken")


@frozen()
class ServerToken(Token):
    client: Client = field(factory=Client)


def by_name_and_password(name: str, password: str) -> Predicate[ServerToken]:
    def predicate(token: ServerToken) -> bool:
        return token.client.name == name and token.client.password == password

    return predicate


TS = TypeVar("TS", bound="AnyTokens")


class Tokens(StringDict[T]):
    def __init__(self, token_type: Type[T]) -> None:
        self._token_type = token_type

    @property
    def token_type(self) -> Type[T]:
        return self._token_type

    def copy(self: TS) -> TS:
        return type(self)(self.token_type)

    def add(self, token: T) -> None:
        self[token.value] = token

    def remove(self, token: T) -> None:
        del self[token.value]


AnyTokens = Tokens[Any]


class ServerTokens(Tokens[ST]):
    def find(self, name: str, password: str) -> Optional[ST]:
        return iter(self.values()).find(by_name_and_password(name, password)).extract()

    async def register(self, name: str, password: str) -> ST:
        token = self.token_type()

        await token.client.login(name, password)

        self.add(token)

        return token

    async def unregister(self, token: ST) -> None:
        await token.client.logout()

        self.remove(token)
