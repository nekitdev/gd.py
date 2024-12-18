from typing_aliases import Unary
from xor_cipher import cyclic_xor

from gd.crypto.base64 import decode_base64, encode_base64
from gd.crypto.enums import CyclicKey
from gd.defaults.encoding import DEFAULT_ENCODING, DEFAULT_ERRORS

__all__ = (
    "encode_robtop",
    "decode_robtop",
    "encode_robtop_string",
    "decode_robtop_string",
    "encode_robtop_with",
    "decode_robtop_with",
    "encode_robtop_string_with",
    "decode_robtop_string_with",
)


def encode_robtop(data: bytes, key: CyclicKey) -> bytes:
    """Encodes the given data using RobTop encoding with the given key.

    Arguments:
        data: The data to encode.
        key: The key to use.

    Returns:
        The encoded data.
    """
    return encode_base64(cyclic_xor(data, key.bytes))


def encode_robtop_with(key: CyclicKey) -> Unary[bytes, bytes]:
    """Returns the unary function that encodes data using RobTop encoding.

    Arguments:
        key: The key to use.

    Returns:
        The unary function that encodes data using RobTop encoding.
    """

    def encode(data: bytes) -> bytes:
        return encode_robtop(data, key)

    return encode


def decode_robtop(data: bytes, key: CyclicKey) -> bytes:
    """Decodes the given data using RobTop encoding with the given key.

    This function is the inverse of [`encode_robtop`][gd.crypto.robtop.encode_robtop], meaning that

    ```python
    decode_robtop(encode_robtop(data, key), key) == data
    ```

    holds for any `data` and `key`.

    Arguments:
        data: The data to decode.
        key: The key to use.

    Returns:
        The decoded data.
    """
    return cyclic_xor(decode_base64(data), key.bytes)


def decode_robtop_with(key: CyclicKey) -> Unary[bytes, bytes]:
    """Returns the unary function that decodes data using RobTop encoding.

    Arguments:
        key: The key to use.

    Returns:
        The unary function that decodes data using RobTop encoding.
    """

    def decode(data: bytes) -> bytes:
        return decode_robtop(data, key)

    return decode


def encode_robtop_string(
    string: str, key: CyclicKey, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`encode_robtop`][gd.crypto.robtop.encode_robtop] to handle string encoding.

    Arguments:
        string: The string to encode.
        key: The key to use.
        encoding: The encoding to use.
        errors: The error handling to use.

    Returns:
        The encoded string.
    """
    return encode_robtop(string.encode(encoding, errors), key).decode(encoding, errors)


def encode_robtop_string_with(
    key: CyclicKey, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> Unary[str, str]:
    """Returns the unary function that encodes strings using RobTop encoding.

    Arguments:
        key: The key to use.
        encoding: The encoding to use.
        errors: The error handling to use.

    Returns:
        The unary function that encodes strings using RobTop encoding.
    """

    def encode_string(string: str) -> str:
        return encode_robtop_string(string, key, encoding, errors)

    return encode_string


def decode_robtop_string(
    string: str, key: CyclicKey, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    """Wraps [`decode_robtop`][gd.crypto.robtop.decode_robtop] to handle string encoding.

    This function is the inverse of [`encode_robtop_string`][gd.crypto.robtop.encode_robtop_string],
    meaning that

    ```python
    decode_robtop_string(encode_robtop_string(string, key), key) == string
    ```

    holds for any `string` and `key`.

    Arguments:
        string: The string to decode.
        key: The key to use.
        encoding: The encoding to use.
        errors: The error handling to use.

    Returns:
        The decoded string.
    """
    return decode_robtop(string.encode(encoding, errors), key).decode(encoding, errors)


def decode_robtop_string_with(
    key: CyclicKey, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> Unary[str, str]:
    """Returns the unary function that decodes strings using RobTop encoding.

    Arguments:
        key: The key to use.
        encoding: The encoding to use.
        errors: The error handling to use.

    Returns:
        The unary function that decodes strings using RobTop encoding.
    """

    def decode_string(string: str) -> str:
        return decode_robtop_string(string, key, encoding, errors)

    return decode_string
