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


class MissingAccess(ClientException):
    """Exception that is raised when server responses with -1."""
    def __init__(self, **params):
        _type = params.get('type')
        _id = params.get('id')
        _message = params.get('message')
        message = f"Missing access to '{_type}' with id: '{_id}'."
        if _message is not None:
            message = _message
        super().__init__(message)


class SongRestrictedForUsage(ClientException):
    """Exception that is raised when server returns -2
    when looking for a song.
    """
    def __init__(self, _id):
        message = f"Song with id '{_id}' is not allowed for use."
        super().__init__(message)


class LoginFailure(ClientException):
    """Exception that is raised when server returns -1
    when trying to log in.
    """
    def __init__(self, login, password):
        self.login = login
        self.password = password
        message = "Failed to login with parameters:\n" \
            f"<login='{self.login}', password='{self.password}'>."
        super().__init__(message)


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
        name = cls_name
        message = f"No <{name}>'s were found."
        super().__init__(message)


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


class PaginatorIsEmpty(PaginatorException):
    """Exception that is raised if :class:`Paginator` is empty.
    Might be deprecated soon.
    """
    # might be deprecated soon
    def __init__(self):
        message = "<gd.Paginator> object has no elements to operate with."
        super().__init__(message)
