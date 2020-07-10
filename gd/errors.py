from gd.typing import Optional


class GDException(Exception):
    """Base exception class for gd.py.
    This could be caught to handle any exceptions thrown from this library.
    """

    pass


class ClientException(GDException):
    """Base exception class for errors that are thrown
    when operation in :class:`Client` fails.
    """

    pass


class ParserError(GDException):
    """Exception that is raised if conversion in :class:`.XMLParser` fails."""

    pass


class EditorError(GDException):
    """Exception that is raised when converting string
    to :class:`.api.Object` or :class:`.api.Editor` failed.
    """

    pass


class HTTPError(ClientException):
    """Exception that is raised when exception
    in :class:`.utils.http.HTTPClient` occurs.
    """

    def __init__(self, exc: Exception) -> None:
        message = (
            "Failed to process HTTP request. "
            "Caused by: Error<{0.__class__.__name__}>({0})".format(exc)
        )
        self._origin = exc
        super().__init__(message)

    @property
    def origin(self) -> Exception:
        """:class:`Exception`: The original exception that was raised."""
        return self._origin


class MissingAccess(ClientException):
    """Exception that is raised when server responses with -1."""

    def __init__(self, message: Optional[str] = None) -> None:
        if message is not None:
            super().__init__(message)

        else:
            super().__init__()


class SongRestrictedForUsage(ClientException):
    """Exception that is raised when server returns -2
    when looking for a song.
    """

    def __init__(self, id: int) -> None:
        message = f"Song with id {id!r} is not allowed to use."
        super().__init__(message)


class LoginFailure(ClientException):
    """Exception that is raised when server returns -1
    when trying to log in.
    """

    def __init__(self, login: str, password: str) -> None:
        self._login = login
        self._password = password

        message = "Failed to login with parameters: " f"login: {login!r}, password: {password!r}."

        super().__init__(message)

    @property
    def login(self) -> str:
        """Username that was wrong or password did not match."""
        return self._login

    @property
    def password(self) -> str:
        """Password that login was failed with."""
        return self._password


class NothingFound(ClientException):
    """Exception that is raised when server returns nothing
    that can be converted to object of name *cls_name*.
    """

    def __init__(self, cls_name: str) -> None:
        self._cls_name = cls_name
        message = f"No <{cls_name}> instances were found."
        super().__init__(message)

    @property
    def cls_name(self) -> str:
        """Name of the class instances of which were not found."""
        return self._cls_name


class NotLoggedError(ClientException):
    """Exception that is raised when a function that requires logged in user is called
    while :class:`Client` is not logged.
    """

    def __init__(self, func_name: Optional[str]) -> None:
        if func_name:
            message = f"{func_name!r} requires client to be logged."
        else:
            message = "Login is required but is missing."
        super().__init__(message)
