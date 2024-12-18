from typing_aliases import Unary

from gd.crypto.enums import CyclicKey, Salt
from gd.crypto.hash import sha1_string
from gd.crypto.robtop import encode_robtop_string
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS

__all__ = ("generate_check", "generate_check_with")


def generate_check(
    string: str,
    key: CyclicKey,
    salt: Salt = Salt.EMPTY,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """Generates the check for the `string` using `key` and `salt`.

    The steps are as follows:

    - Hash the `string` with `salt` via [`sha1_string`][gd.crypto.hash.sha1_string];
    - Encode the hash with `key` via [`encode_robtop_string`][gd.crypto.robtop.encode_robtop_string].

    `encoding` and `errors` are used to handle the encoding of the string.

    Arguments:
        string: The string to generate the check for.
        key: The key to use.
        salt: The salt to use.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The generated check string.
    """
    return encode_robtop_string(sha1_string(string, salt, encoding, errors), key, encoding, errors)


def generate_check_with(
    key: CyclicKey,
    salt: Salt = Salt.EMPTY,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> Unary[str, str]:
    """Returns the unary function that calls [`generate_check`][gd.crypto.checks.generate_check]
    with the given `key`, `salt`, `encoding` and `errors`.

    Arguments:
        key: The key to use.
        salt: The salt to use.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The function that generates the check for the given string.
    """

    def generate(string: str) -> str:
        return generate_check(string, key, salt, encoding, errors)

    return generate
