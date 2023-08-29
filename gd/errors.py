from __future__ import annotations

from typing import Generic, Optional, TypeVar

from attrs import frozen
from named import get_type_name
from pendulum import Duration
from typing_aliases import AnyError, NormalError

from gd.string_utils import tick

__all__ = (
    "InternalError",
    "GDError",
    "HTTPError",
    "HTTPErrorWithOrigin",
    "HTTPStatusError",
    "ClientError",
    "MissingAccess",
    "SongRestricted",
    "CommentBanned",
    "LoginFailed",
    "LoginRequired",
    "NothingFound",
)

T = TypeVar("T")
U = TypeVar("U")


class InternalError(RuntimeError):
    pass


class GDError(NormalError):
    pass


class HTTPError(GDError):
    pass


E = TypeVar("E", bound=AnyError, covariant=True)


FAILED_TO_PROCESS = "failed to process HTTP request. {}: {}"


@frozen()
class HTTPErrorWithOrigin(Generic[E], HTTPError):
    origin: E

    def __init__(self, origin: E) -> None:
        super().__init__(FAILED_TO_PROCESS.format(get_type_name(origin), origin))

        self.__attrs_init__(origin)  # type: ignore


HTTP_STATUS = "HTTP {}"


@frozen()
class HTTPStatusError(HTTPError):
    status: int

    def __init__(self, status: int) -> None:
        super().__init__(HTTP_STATUS.format(self.status))

        self.__attrs_init__(status)  # type: ignore


class ClientError(GDError):
    pass


class MissingAccess(ClientError):
    pass


SONG_RESTRICTED = "song with ID {} is not allowed for use"


@frozen()
class SongRestricted(ClientError):
    song_id: int

    def __init__(self, song_id: int) -> None:
        super().__init__(SONG_RESTRICTED.format(tick(song_id)))

        self.__attrs_init__(song_id)  # type: ignore


LOGIN_FAILED = "login failed with name {} and password {}"


@frozen()
class LoginFailed(ClientError):
    name: str
    password: str

    def __init__(self, name: str, password: str) -> None:
        super().__init__(LOGIN_FAILED.format(tick(name), tick(password)))

        self.__attrs_init__(name, password)  # type: ignore


PERMANENT = "permanently banned from posting comments; reason: {}"
TEMPORARY = "banned for {} from posting comments; reason: {}"
DEFAULT_REASON = "not provided"


@frozen()
class CommentBanned(ClientError):
    timeout: Optional[Duration] = None
    reason: Optional[str] = None

    def __init__(self, timeout: Optional[Duration] = None, reason: Optional[str] = None) -> None:
        if reason is None:
            reason = DEFAULT_REASON

        if timeout is None:
            message = PERMANENT.format(reason)

        else:
            message = TEMPORARY.format(timeout, reason)

        super().__init__(message)

        self.__attrs_init__(timeout, reason)  # type: ignore


class LoginRequired(ClientError):
    pass


NOTHING_FOUND = "{} not found"


@frozen()
class NothingFound(ClientError):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(NOTHING_FOUND.format(tick(name)))

        self.__attrs_init__(name)  # type: ignore
