from gd.errors import GDError

__all__ = (
    "AuthenticationError",
    "AuthenticationInvalid",
    "AuthenticationMissing",
    "AuthenticationNotFound",
)


class AuthenticationError(GDError):
    """Authentication has failed."""


AUTHENTICATION_INVALID = "authentication is invalid"


class AuthenticationInvalid(AuthenticationError):
    """Authentication is invalid."""

    def __init__(self) -> None:
        super().__init__(AUTHENTICATION_INVALID)


AUTHENTICATION_MISSING = "authentication is missing"


class AuthenticationMissing(AuthenticationError):
    """Authentication is missing."""

    def __init__(self) -> None:
        super().__init__(AUTHENTICATION_MISSING)


AUTHENTICATION_NOT_FOUND = "authentication token was not found"


class AuthenticationNotFound(AuthenticationError):
    """Authentication token was not found."""

    def __init__(self) -> None:
        super().__init__(AUTHENTICATION_NOT_FOUND)
