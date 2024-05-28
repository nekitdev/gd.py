from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Optional, TypeVar

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
failed_to_process = FAILED_TO_PROCESS.format


class HTTPErrorWithOrigin(Generic[E], HTTPError):
    def __init__(self, origin: E) -> None:
        super().__init__(failed_to_process(get_type_name(origin), origin))

        self._origin = origin

    @property
    def origin(self) -> E:
        return self._origin


HTTP_STATUS = "HTTP {}"
http_status = HTTP_STATUS.format


class HTTPStatusError(HTTPError):
    def __init__(self, status: int) -> None:
        super().__init__(HTTP_STATUS.format(status))

        self._status = status

    @property
    def status(self) -> int:
        return self._status


class ClientError(GDError):
    pass


class MissingAccess(ClientError):
    pass


SONG_RESTRICTED = "song with ID `{}` is not allowed for use"
song_restricted = SONG_RESTRICTED.format


class SongRestricted(ClientError):
    def __init__(self, song_id: int) -> None:
        super().__init__(song_restricted(song_id))

        self._song_id = song_id

    @property
    def song_id(self) -> int:
        return self._song_id


LOGIN_FAILED = "login failed with name `{}` and password `{}`"
login_failed = LOGIN_FAILED.format


class LoginFailed(ClientError):
    def __init__(self, name: str, hashed_password: str) -> None:
        super().__init__(login_failed(name, hashed_password))

        self._name = name
        self._hashed_password = hashed_password

@frozen()
class CloudFlareError(ClientError):
    error_code:int
    
    @classmethod
    def from_str(cls, error:str):
        return cls(int(error.split(":")[1])



PERMANENT = "permanently banned from posting comments; reason: `{}`"
permanent = PERMANENT.format

TEMPORARY = "banned for `{}` from posting comments; reason: `{}`"
temporary = TEMPORARY.format

DEFAULT_REASON = "not provided"


class CommentBanned(ClientError):
    def __init__(self, timeout: Optional[Duration] = None, reason: Optional[str] = None) -> None:
        if reason is None:
            reason = DEFAULT_REASON

        if timeout is None:
            message = permanent(reason)

        else:
            message = temporary(timeout, reason)

        super().__init__(message)

        self._timeout = timeout
        self._reason = reason

    @property
    def timeout(self) -> Optional[Duration]:
        return self._timeout

    @property
    def reason(self) -> str:
        return self._reason


class LoginRequired(ClientError):
    pass


NOTHING_FOUND = "`{}` not found"
nothing_found = NOTHING_FOUND.format


class NothingFound(ClientError):
    def __init__(self, name: str) -> None:
        super().__init__(nothing_found(name))

        self._name = name

    @property
    def name(self) -> str:
        return self._name
