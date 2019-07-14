class GDException(Exception):
    """Base exception class for gd.py

    This could be caught to handle any exceptions thrown from this library.
    """
    pass


class ClientException(GDException):
    """Base exception class for errors that are thrown,

    when operation in :class:`Client` fails.
    """
    pass


class PaginatorException(GDException):
    """Base exception class for errors that are thrown,

    when operating with :class:`Paginator`.
    """
    pass


class MissingAccess(ClientException):
    def __init__(self, **params):
        _type = params.get('type')
        _id = params.get('id')
        message = f"Missing access to '{_type}' with id: '{_id}'."
        super().__init__(message)


class SongRestrictedForUsage(ClientException):
    def __init__(self, _id):
        message = f"Song with id '{_id}' is not allowed for use."
        super().__init__(message)


class LoginFailure(ClientException):
    def __init__(self, **params):
        self.login = params.get('login')
        self.password = params.get('password')
        message = f"Failed to login with parameters:\n<login='{self.login}', password='{self.password}'>."
        super().__init__(message)


class NothingFound(ClientException):
    def __init__(self, cls):
        self.type = cls.__name__.lower()
        message = f"No <{self.type}>'s were found."
        super().__init__(message)


class PagesOutOfRange(PaginatorException):
    def __init__(self, **params):
        _page_num = params.get('page')
        _info = params.get('info')
        if str(_info).isdigit():
            message = f"Pages are out of range.\nRequested page: '{_page_num}', Pages existing: '{_info}'"
        else:
            message = f"{_info}\nRequested page: '{_page_num}'"
        super().__init__(message)


class PaginatorIsEmpty(PaginatorException):
    def __init__(self):
        message = "'gd.Paginator' object has no elements to operate with."
        super().__init__(message)

# TO_DO: finish documenting, work with logic and refactor code in core
