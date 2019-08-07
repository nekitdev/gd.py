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


class PaginatorException(GDException):
    """Base exception class for errors that are thrown
    when operating with :class:`Paginator` gets an error.
    """
    pass


class FailedConversion(GDException):
    """Exception that is raised when Enum converter
    fails to turn given value into requested Enum.
    """
    def __init__(self, enum, value):
        self._enum = enum
        self._value = value
        message = f'Failed to convert value {value!r} to enum: {enum!r}.'
        super().__init__(message)

    @property
    def enum(self):
        return self._enum

    @property
    def value(self):
        return self._value
    

class HTTPNotConnected(ClientException):
    """Exception that is raised when exception
    in :class:`.utils.http.HTTPClient` occurs.
    """
    def __init__(self):
        message = 'Internet connection failed.'
        super().__init__(message)


class FailedCaptcha(ClientException):
    """Exception that is raised when unknown results
    when solving GD Captcha are recieved.
    """
    def __init__(self, msg):
        message = f'Solving Captcha failed. {msg}'
        super().__init__(message)


class MissingAccess(ClientException):
    """Exception that is raised when server responses with -1."""
    def __init__(self, *, type: str = None, id: int = None, message: str = None):
        message = (
            f"Missing access to {type!r} with id: {id!r}."
            if message is None else message
        )
        super().__init__(message)


class SongRestrictedForUsage(ClientException):
    """Exception that is raised when server returns -2
    when looking for a song.
    """
    def __init__(self, id):
        message = f"Song with id {id!r} is not allowed for use."
        super().__init__(message)


class LoginFailure(ClientException):
    """Exception that is raised when server returns -1
    when trying to log in.
    """
    def __init__(self, login, password):
        self._login = login
        self._password = password
        message = "Failed to login with parameters:\n" \
            f"<login='{self.login}', password='{self.password}'>."
        super().__init__(message)

    @property
    def login(self):
        """Username that was wrong or password did not match."""
        return self._login

    @property
    def password(self):
        """Password that login was failed with."""
        return self._password


class FailedToChange(ClientException):
    """Exception that is raised when logged in :class:`Client`
    fails to change its password or username.
    """
    def __init__(self, typeof):
        message = f"Failed to change {typeof}. Reason: Unspecified"  # [Future]
        super().__init__(message)


class NothingFound(ClientException):
    """Exception that is raised when server returns nothing
    that can be converted to object of name *cls_name*.
    """
    def __init__(self, cls_name):
        self._cls_name = cls_name
        message = f"No <{cls_name}>'s were found."
        super().__init__(message)

    @property
    def cls_name(self):
        """Name of the class instances of which were not found."""
        return self._cls_name


class NotLoggedError(ClientException):
    """Exception that is raised when a function that requires logged in user is called
    while :class:`Client` is not logged.
    """
    def __init__(self, func_name):
        message = f"'{func_name}' requires client to be logged."
        super().__init__(message)


class PagesOutOfRange(PaginatorException):
    """Exception that is raised if a non-existing page
    is requested in :class:`Paginator`.
    """
    def __init__(self, page, info):
        if str(info).isdigit():
            message = f"Pages are out of range.\nRequested page: '{page}', Pages existing: '{info}'"
        else:
            message = f"{info}\nRequested page: '{page_num}'"
        super().__init__(message)
