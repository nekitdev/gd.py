from typing import AnyStr

from gd.crypto.base64 import decode_base64_url_safe, encode_base64_url_safe
from gd.crypto.zip import compress, decompress
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS

__all__ = (
    "zip_level",
    "unzip_level",
    "zip_level_string",
    "unzip_level_string",
    "generate_level_seed",
    "generate_level_leaderboard_seed",
)


def zip_level(data: bytes) -> bytes:
    """Compresses and encodes the level data.

    Arguments:
        data: The level data to compress and encode.

    Returns:
        The compressed and encoded level data.
    """
    return encode_base64_url_safe(compress(data))


def unzip_level(data: bytes) -> bytes:
    """Decodes the level data and decompresses it.

    This is the inverse of [`zip_level`][gd.crypto.levels.zip_level], meaning that

    ```python
    unzip_level(zip_level(data)) == data
    ```

    holds for any `data`.

    Arguments:
        data: The level data to decode and decompress.

    Returns:
        The decoded and decompressed level data.
    """
    return decompress(decode_base64_url_safe(data))


def zip_level_string(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`zip_level`][gd.crypto.levels.zip_level] to handle string encoding.

    Arguments:
        string: The level string to compress and encode.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The compressed and encoded level string.
    """
    return zip_level(string.encode(encoding, errors)).decode(encoding, errors)


def unzip_level_string(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`unzip_level`][gd.crypto.levels.unzip_level] to handle string encoding.

    This function is the inverse of [`zip_level_string`][gd.crypto.levels.zip_level_string],
    meaning that

    ```python
    unzip_level_string(zip_level_string(string)) == string
    ```

    holds for any `string`.

    Arguments:
        string: The level string to decode and decompress.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The decoded and decompressed level string.
    """
    return unzip_level(string.encode(encoding, errors)).decode(encoding, errors)


DEFAULT_LENGTH = 50
"""The default length of the level seed."""


def generate_level_seed(data: AnyStr, length: int = DEFAULT_LENGTH) -> AnyStr:
    """Generates the seed for the given level data.

    See the source code for more information.

    Arguments:
        data: The level data to generate the seed for.
        length: The length of the seed.

    Returns:
        The seed for the given level data.
    """
    data_length = len(data)

    if data_length < length:
        return data

    return data[:: data_length // length][:length]


CHECK_MULTIPLY = 1482
ATTEMPTS_ADD = 8354
CLICKS_ADD = 3991
RECORD_ADD = 8354
SECONDS_ADD = 4085
COINS_ADD = 5819

TOTAL_SUBTRACT = CLICKS_ADD * RECORD_ADD + SECONDS_ADD * SECONDS_ADD

DEFAULT_CLICKS = 0
"""The default amount of clicks made."""
DEFAULT_RECORD = 0
"""The default record achieved."""
DEFAULT_SECONDS = 0
"""The default time in seconds."""
DEFAULT_CHECK = True
"""The default value for whether the record has passed checks."""


def generate_level_leaderboard_seed(
    clicks: int = DEFAULT_CLICKS,
    record: int = DEFAULT_RECORD,
    seconds: int = DEFAULT_SECONDS,
    check: bool = DEFAULT_CHECK,
) -> int:
    """Generates the seed for the level leaderboard.

    See the source code for more information.

    Arguments:
        clicks: The amount of clicks made.
        record: The record achieved.
        seconds: The time in seconds.
        check: Whether the record has passed checks.

    Returns:
        The seed for the level leaderboard.
    """
    seconds_added = seconds + SECONDS_ADD

    return (
        CHECK_MULTIPLY * check
        + (clicks + CLICKS_ADD) * (record + RECORD_ADD)
        + seconds_added * seconds_added
        - TOTAL_SUBTRACT
    )
