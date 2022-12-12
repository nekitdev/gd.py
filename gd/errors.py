from datetime import timedelta
from typing import Any, Generic, Optional, TypeVar

from named import get_type_name

from gd.string_utils import password_str, tick
from gd.typing import AnyException

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


class GDError(Exception):
    pass


class HTTPError(GDError):
    pass


E = TypeVar("E", bound=AnyException, covariant=True)


FAILED_TO_PROCESS = "failed to process HTTP request. {}: {}"


class HTTPErrorWithOrigin(Generic[E], HTTPError):
    def __init__(self, origin: E) -> None:
        self._origin = origin

        super().__init__(FAILED_TO_PROCESS.format(get_type_name(origin)), origin)

    @property
    def origin(self) -> E:
        return self._origin


STATUS_REASON = "{} {}"


class HTTPStatusError(HTTPError):
    def __init__(self, status: int, reason: Optional[Any]) -> None:
        self._status = status
        self._reason = reason

        super().__init__(STATUS_REASON.format(status, reason))

    @property
    def status(self) -> int:
        return self._status

    @property
    def reason(self) -> Optional[Any]:  # type: ignore
        return self._reason


class ClientError(GDError):
    pass


class MissingAccess(ClientError):
    pass


SONG_RESTRICTED = "song with id {} is not allowed for use"


class SongRestricted(ClientError):
    def __init__(self, id: int) -> None:
        self._id = id

        super().__init__(SONG_RESTRICTED.format(tick(id)))

    @property
    def id(self) -> int:
        return self._id


LOGIN_FAILED = "login failed with name {} and password {}"


class LoginFailed(ClientError):
    def __init__(self, name: str, password: str) -> None:
        password = password_str(password)

        self._name = name
        self._password = password

        super().__init__(LOGIN_FAILED.format(tick(name), tick(password)))

    @property
    def name(self) -> str:
        return self._name

    @property
    def password(self) -> str:
        return self._password


class CommentBanned(ClientError):
    PERMANENT = "permanently banned from posting comments; reason: {}"
    TEMPORARY = "banned for {} from posting comments; reason: {}"
    DEFAULT_REASON = "not provided"

    def __init__(self, timeout: Optional[timedelta] = None, reason: Optional[str] = None) -> None:
        self._timeout = timeout
        self._reason = reason

        super().__init__(self.message)

    @property
    def timeout(self) -> Optional[timedelta]:
        return self._timeout

    @property
    def reason(self) -> Optional[str]:
        return self._reason

    @property
    def message(self) -> str:
        timeout = self.timeout
        reason = self.reason

        if reason is None:
            reason = self.DEFAULT_REASON

        if timeout is None:
            return self.PERMANENT.format(reason)

        return self.TEMPORARY.format(timeout, reason)


class LoginRequired(ClientError):
    pass


NOTHING_FOUND = "{} not found"


class NothingFound(ClientError):
    def __init__(self, name: str) -> None:
        self._name = name

        super().__init__(NOTHING_FOUND.format(tick(name)))

    @property
    def name(self) -> str:
        return self._name
