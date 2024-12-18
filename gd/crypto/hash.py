from hashlib import sha1 as standard_sha1

from gd.crypto.enums import Salt
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS

__all__ = ("sha1", "sha1_string")


def sha1(data: bytes, salt: Salt = Salt.EMPTY) -> str:
    """Hashes the `data` combined with `salt` using the SHA-1 algorithm.

    Arguments:
        data: The data to hash.
        salt: The salt to use.

    Returns:
        The digest string.
    """
    return standard_sha1(data + salt.bytes).digest().hex()


def sha1_string(
    string: str,
    salt: Salt = Salt.EMPTY,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """Wraps the [`sha1`][gd.crypto.hash.sha1] function to handle string encoding.

    Arguments:
        string: The string to hash.
        salt: The salt to use.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The digest string.
    """
    return sha1(string.encode(encoding, errors), salt)
