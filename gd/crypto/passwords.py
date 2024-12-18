from gd.crypto.enums import Salt
from gd.crypto.hash import sha1_string
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS

__all__ = ("hash_password",)


def hash_password(
    password: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Hashes the `password`.

    This is equivalent to calling [`sha1_string`][gd.crypto.hash.sha1_string]
    with the [`PASSWORD`][gd.crypto.enums.Salt.PASSWORD] salt.

    Arguments:
        password: The password to hash.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The hashed password.
    """
    return sha1_string(password, Salt.PASSWORD, encoding, errors)
