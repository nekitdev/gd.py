from base64 import b64decode as standard_decode_base64
from base64 import b64encode as standard_encode_base64
from base64 import urlsafe_b64decode as standard_decode_base64_url_safe
from base64 import urlsafe_b64encode as standard_encode_base64_url_safe
from typing import Literal

from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS

__all__ = (
    "BASE64_PAD",
    "BASE64_PADDING",
    "BASE64_INVALID_TO_PAD",
    "enforce_valid_base64",
    "decode_base64",
    "encode_base64",
    "decode_base64_url_safe",
    "encode_base64_url_safe",
    "decode_base64_string",
    "encode_base64_string",
    "decode_base64_string_url_safe",
    "encode_base64_string_url_safe",
)

BASE64_PAD: Literal[4] = 4
"""The padding used in Base64."""
BASE64_PADDING: Literal[b"="] = b"="
"""The padding byte in Base64."""
BASE64_INVALID_TO_PAD: Literal[1] = 1
"""The Base64 data is invalid if `length % 4 = 1`."""


def drop_last(count: int, data: bytes) -> bytes:
    return data[:-count]


def enforce_valid_base64(data: bytes) -> bytes:
    """Enforces `data` to be valid Base64.

    If `length % 4` is `1`, the last byte is dropped.
    Otherwise, padding is appended to the data if needed.
    Therefore, the data is guaranteed to be valid Base64.

    Arguments:
        data: The Base64 data to enforce validitiy on.

    Returns:
        The valid Base64 data.
    """
    pad = BASE64_PAD
    padding = BASE64_PADDING
    invalid_to_pad = BASE64_INVALID_TO_PAD

    required = len(data) % pad

    if required:
        if required == invalid_to_pad:
            data = drop_last(invalid_to_pad, data)

        else:
            data += padding * (pad - required)

    return data


def decode_base64(data: bytes) -> bytes:
    """Decodes Base64 `data`, enforcing its validity using
    [`enforce_valid_base64`][gd.crypto.base64.enforce_valid_base64].

    Arguments:
        data: The Base64 data to decode.

    Returns:
        The decoded data.
    """
    return standard_decode_base64(enforce_valid_base64(data))


def encode_base64(data: bytes) -> bytes:
    """Encodes `data` to Base64.

    Arguments:
        data: The data to encode.

    Returns:
        The Base64 encoded data.
    """
    return standard_encode_base64(data)


def decode_base64_url_safe(data: bytes) -> bytes:
    """Decodes URL-safe Base64 `data`, enforcing its validity using
    [`enforce_valid_base64`][gd.crypto.base64.enforce_valid_base64].

    Arguments:
        data: The URL-safe Base64 data to decode.

    Returns:
        The decoded data.
    """
    return standard_decode_base64_url_safe(enforce_valid_base64(data))


def encode_base64_url_safe(data: bytes) -> bytes:
    """Encodes `data` to URL-safe Base64.

    Arguments:
        data: The data to encode.

    Returns:
        The URL-safe Base64 encoded data.
    """
    return standard_encode_base64_url_safe(data)


def decode_base64_string(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`decode_base64`][gd.crypto.base64.decode_base64] to handle string encoding.

    Arguments:
        string: The Base64 string to decode.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The decoded string.
    """
    return decode_base64(string.encode(encoding, errors)).decode(encoding, errors)


def encode_base64_string(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`encode_base64`][gd.crypto.base64.encode_base64] to handle string encoding.

    Arguments:
        string: The string to encode.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The Base64 encoded string.
    """
    return encode_base64(string.encode(encoding, errors)).decode(encoding, errors)


def decode_base64_string_url_safe(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`decode_base64_url_safe`][gd.crypto.base64.decode_base64_url_safe]
    to handle string encoding.

    Arguments:
        string: The URL-safe Base64 string to decode.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The decoded string.
    """
    return decode_base64_url_safe(string.encode(encoding, errors)).decode(encoding, errors)


def encode_base64_string_url_safe(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`encode_base64_url_safe`][gd.crypto.base64.encode_base64_url_safe]
    to handle string encoding.

    Arguments:
        string: The string to encode.
        encoding: The encoding to use.
        errors: The errors strategy to use.

    Returns:
        The URL-safe Base64 encoded string.
    """
    return encode_base64_url_safe(string.encode(encoding, errors)).decode(encoding, errors)
