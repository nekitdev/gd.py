from random import choices
from random import randrange as random_range
from string import ascii_letters, digits

from gd.crypto.enums import CyclicKey
from gd.crypto.robtop import encode_robtop_string
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS
from gd.strings.concatenation import concat_empty

__all__ = (
    "DEFAULT_CHARACTERS",
    "DEFAULT_LENGTH",
    "DEFAULT_LENGTH_WITH_VALUE",
    "DEFAULT_START",
    "DEFAULT_STOP",
    "generate_encode_random_value",
    "generate_random_string",
    "generate_random_string_append_value",
)

DEFAULT_CHARACTERS = ascii_letters + digits
"""Default characters to use for random string generation."""

DEFAULT_LENGTH = 10
"""Default length of random strings to generate."""


def generate_random_string(
    length: int = DEFAULT_LENGTH, characters: str = DEFAULT_CHARACTERS
) -> str:
    """Generates random strings of given `length` from `characters`.

    Arguments:
        length: The length of the string to generate.
        characters: The characters to use.

    Returns:
        The generated string.
    """
    return concat_empty(choices(characters, k=length))


DEFAULT_START = 1_000
"""The default random value range start."""

DEFAULT_STOP = 1_000_000
"""The default random value range stop."""


def generate_encode_random_value(
    key: CyclicKey,
    start: int = DEFAULT_START,
    stop: int = DEFAULT_STOP,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """Generates some random value in `[start, stop)` range and encodes it with `key`.

    Arguments:
        key: The key to use.
        start: The start of the range.
        stop: The stop of the range.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The encoded random value.
    """
    return encode_robtop_string(str(random_range(start, stop)), key, encoding, errors)


DEFAULT_LENGTH_WITH_VALUE = 5
"""The default length of the string to generate with value."""


def generate_random_string_append_value(
    key: CyclicKey,
    length: int = DEFAULT_LENGTH_WITH_VALUE,
    characters: str = DEFAULT_CHARACTERS,
    start: int = DEFAULT_START,
    stop: int = DEFAULT_STOP,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """Combines [`generate_random_string`][gd.crypto.random.generate_random_string] and
    [`generate_encode_random_value`][gd.crypto.random.generate_encode_random_value].

    Arguments:
        key: The key to use.
        length: The length of the string to generate.
        characters: The characters to use.
        start: The start of the range.
        stop: The stop of the range.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The generated string with encoded random value appended.
    """
    return generate_random_string(length, characters) + generate_encode_random_value(
        key, start, stop, encoding, errors
    )
