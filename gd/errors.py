from gd.typing import TYPE_CHECKING, Any, Optional, TypeVar

__all__ = (
    "GDException",
    "HTTPException",
    "HTTPError",
    "HTTPStatusError",
    "ClientException",
    "MissingAccess",
    "SongRestricted",
    "LoginFailure",
    "LoginRequired",
    "NothingFound",
    "DataException",
    "DeError",
    "SerError",
    "XMLError",
    "EditorError",
)

T = TypeVar("T")
U = TypeVar("U")

if TYPE_CHECKING:
    from gd.model_backend import Field  # type: ignore  # noqa


class GDException(Exception):
    """Base exception class for gd.py.
    This could be caught to handle any exceptions thrown from this library.
    """

    pass


class HTTPException(GDException):
    """Base exception class for errors that are thrown
    when operation in :class:`~gd.HTTPClient` fails.
    """

    pass


class HTTPError(HTTPException):
    """Exception that is raised when exception
    in :class:`~gd.HTTPClient` occurs.
    """

    def __init__(self, origin: BaseException) -> None:
        self._origin = origin

        super().__init__(f"Failed to process HTTP request. {type(origin).__name__}: {origin}")

    @property
    def origin(self) -> BaseException:
        """:class:`BaseException`: The original exception that was raised."""
        return self._origin


class HTTPStatusError(HTTPException):
    """Exception that is raised when error status code is returned.
    Error codes are considered to be ``4XX`` (client errors) and ``5XX`` (server errors).
    """

    def __init__(self, status: int, reason: Optional[Any]) -> None:
        self._status = status
        self._reason = reason

        super().__init__(f"{status} {reason}")

    @property
    def status(self):
        return self._status

    @property
    def reason(self):
        return self._reason


class ClientException(GDException):
    """Base exception class for errors that are thrown
    when operation in :class:`~gd.Client` fails.
    """

    pass


class MissingAccess(ClientException):
    """Exception that is raised when server responses with an error."""

    pass


class SongRestricted(ClientException):
    """Exception that is raised when server returns an error when looking for a song."""

    def __init__(self, id: int) -> None:
        self._id = id

        super().__init__(f"Song with id {id!r} is not allowed for use.")

    @property
    def id(self) -> int:
        """ID of the song that is restricted."""
        return self._id


class LoginFailure(ClientException):
    """Exception that is raised when server returns an error
    when trying to log in.
    """

    def __init__(self, name: str, password: str) -> None:
        self._name = name
        self._password = password

        super().__init__(f"Failed to login with credentials: {name!r} -> {password!r}.")

    @property
    def name(self) -> str:
        """Username that was wrong or password did not match."""
        return self._name

    @property
    def password(self) -> str:
        """Password that login was failed with."""
        return self._password


class LoginRequired(ClientException):
    """Exception that is raised when the client is not logged in when required."""

    pass


class NothingFound(ClientException):
    """Exception that is raised when server returns nothing.
    It is raised by :class:`~gd.HTTPClient`,
    and automatically handled by :class:`~gd.Client`.

    So, if one is working on lower level, i.e.
    :class:`~gd.HTTPClient` or :class:`~gd.Session`,
    they should handle it as well.
    """

    def __init__(self, instance_name: str) -> None:
        self._instance_name = instance_name

        super().__init__(f"No {instance_name!r} instances were found.")

    @property
    def instance_name(self) -> str:
        """Name of the class instances of which were not found."""
        return self._instance_name


class DataException(GDException):
    """Base exception class for errors that are raised
    when parsing RobTop's data fails.
    """

    pass


class SerError(DataException):
    """Exception that is raised when serializing data fails."""

    def __init__(
        self, data: T, index: U, field: Optional["Field"], origin: Optional[BaseException],
    ) -> None:
        self._data = data
        self._index = index
        self._field = field
        self._origin = origin

        lines = [f"Failed to serialize {data!r} at index {index!r}."]

        if field:
            lines.append(f"[Type] {type(data)!r} -> {field.type!r}")
            lines.append(f"[Function] {field.ser!r}")

        if origin:
            lines.append(f"[Origin] {type(origin).__name__}: {origin}")

        super().__init__("\n".join(lines))

    @property
    def data(self) -> T:
        return self._data

    @property
    def index(self) -> U:
        return self._index  # type: ignore

    @property
    def field(self) -> Optional["Field"]:
        return self._field

    @property
    def origin(self) -> Optional[BaseException]:
        return self._origin


class DeError(DataException):
    """Exception that is raised if deserializing data fails."""

    def __init__(
        self, data: str, index: U, field: Optional["Field"], origin: Optional[BaseException],
    ) -> None:
        self._data = data
        self._index = index
        self._field = field
        self._origin = origin

        lines = [f"Failed to deserialize {data!r} at index {index!r}."]

        if field:
            lines.append(f"[Type] {type(data)!r} -> {field.type!r}")
            lines.append(f"[Function] {field.de!r}")

        if origin:
            lines.append(f"[Origin] {type(origin).__name__}: {origin}")

        super().__init__("\n".join(lines))

    @property
    def data(self) -> str:
        return self._data

    @property
    def index(self) -> U:
        return self._index  # type: ignore

    @property
    def field(self) -> Optional["Field"]:
        return self._field

    @property
    def origin(self) -> Optional[BaseException]:
        return self._origin


class XMLError(DataException):
    """Exception that is raised if conversion in :class:`~gd.XMLParser` fails."""

    pass


class EditorError(DataException):
    """Exception that is raised when converting string in :class:`~gd.api.Editor` failed."""

    pass
