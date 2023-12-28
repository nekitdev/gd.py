from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Optional, TypeVar

from attrs import frozen
from named import get_type_name
from typing_aliases import AnyError, NormalError

if TYPE_CHECKING:
    from pendulum import Duration

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
        super().__init__(HTTP_STATUS.format(status))

        self.__attrs_init__(status)  # type: ignore


class ClientError(GDError):
    pass


class MissingAccess(ClientError):
    pass


SONG_RESTRICTED = "song with ID `{}` is not allowed for use"
song_restricted = SONG_RESTRICTED.format


@frozen()
class SongRestricted(ClientError):
    song_id: int

    def __init__(self, song_id: int) -> None:
        super().__init__(song_restricted(song_id))

        self.__attrs_init__(song_id)  # type: ignore


LOGIN_FAILED = "login failed with name `{}` and password `{}`"
login_failed = LOGIN_FAILED.format


@frozen()
class LoginFailed(ClientError):
    name: str
    password: str

    def __init__(self, name: str, password: str) -> None:
        super().__init__(login_failed(name, password))

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


NOTHING_FOUND = "`{}` not found"
nothing_found = NOTHING_FOUND.format


@frozen()
class NothingFound(ClientError):
    name: str

    def __init__(self, name: str) -> None:
        super().__init__(nothing_found(name))

        self.__attrs_init__(name)  # type: ignore
