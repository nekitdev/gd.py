import secrets
import types

from gd.client import Client, LoginContextManager
from gd.text_utils import make_repr
from gd.typing import Any, Dict, Iterable, Optional, Type

__all__ = ("Token", "TokenDatabase")

TOKEN_LENGTH = 32


class Token:
    def __init__(self, name: str, password: str, token: Optional[str] = None) -> None:
        self._name = name
        self._password = password

        if token is None:
            token = self.create_token()

        self._token = token

    def __repr__(self) -> str:
        info = {"token": self.token}

        return make_repr(self, info)

    def __str__(self) -> str:
        return self.token

    def __hash__(self) -> int:
        return hash(self.token)

    def __eq__(self, other: Any) -> bool:
        return self.token == other

    def __ne__(self, other: Any) -> bool:
        return self.token != other

    @property
    def name(self) -> str:
        return self._name

    @property
    def password(self) -> str:
        return self._password

    @property
    def token(self) -> str:
        return self._token

    @staticmethod
    def create_token(length: int = TOKEN_LENGTH) -> str:
        return secrets.token_hex(length)

    def into(self, client: Client) -> LoginContextManager:
        return client.login(self.name, self.password)

    def into_unsafe(self, client: Client) -> LoginContextManager:
        return client.unsafe_login(self.name, self.password)


class TokenDatabase(Dict[str, Token]):
    def __init__(self, cls: Type[Token] = Token) -> None:
        self.cls = cls

    @property
    def plain_tokens(self) -> Iterable[str]:
        return self.keys()

    @property
    def tokens(self) -> Iterable[Token]:
        return self.values()

    def add(self, name: str, password: str) -> None:
        token = self.cls(name, password)

        self[token.token] = token

    def remove(self, token: str) -> None:
        try:
            del self[token]

        except KeyError:
            pass
