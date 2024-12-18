from xor_cipher import xor

from gd.crypto.aes import decrypt_aes, encrypt_aes
from gd.crypto.base64 import decode_base64_url_safe, encode_base64_url_safe
from gd.crypto.enums import Key
from gd.crypto.zip import compress, decompress

__all__ = (
    "encode_darwin_save",
    "decode_darwin_save",
    "apply_xor",
    "encode_save",
    "encode_save_apply_xor",
    "decode_save",
    "decode_save_apply_xor",
)


def encode_darwin_save(data: bytes) -> bytes:
    """Encodes save data for [`DARWIN`][gd.system.Platform.DARWIN].

    Arguments:
        data: The data to encode.

    Returns:
        The encoded data.
    """
    return encrypt_aes(data)


def decode_darwin_save(data: bytes) -> bytes:
    """Decodes save data for [`DARWIN`][gd.system.Platform.DARWIN].

    This function is the inverse of [`encode_darwin_save`][gd.crypto.saves.encode_darwin_save],
    meaning that

    ```python
    decode_darwin_save(encode_darwin_save(data)) == data
    ```

    holds for any `data`.

    Arguments:
        data: The data to decode.

    Returns:
        The decoded data.
    """
    return decrypt_aes(data)


def apply_xor(data: bytes, key: Key = Key.SAVE) -> bytes:
    """Applies XOR cipher to the `data` using `key`.

    This function is the inverse of itself, meaning that

    ```python
    apply_xor(apply_xor(data, key), key) == data
    ```

    holds for any `data` and `key`.

    Arguments:
        data: The data to apply the cipher to.
        key: The key to use.

    Returns:
        The data after applying the cipher.
    """
    return xor(data, key.value)


def encode_save(data: bytes) -> bytes:
    """Encodes save data.

    Arguments:
        data: The data to encode.

    Returns:
        The encoded data.
    """
    return encode_base64_url_safe(compress(data))


def encode_save_apply_xor(data: bytes, key: Key = Key.SAVE) -> bytes:
    """Same as [`encode_save`][gd.crypto.saves.encode_save], but calls
    [`apply_xor`][gd.crypto.saves.apply_xor] with `key` after encoding.

    Arguments:
        data: The data to encode.
        key: The key to use.

    Returns:
        The encoded data.
    """
    return apply_xor(encode_save(data), key)


def decode_save(data: bytes) -> bytes:
    """Decodes save data.

    This function is the inverse of [`encode_save`][gd.crypto.saves.encode_save], meaning that

    ```python
    decode_save(encode_save(data)) == data
    ```

    holds for any `data`.

    Arguments:
        data: The data to decode.

    Returns:
        The decoded data.
    """
    return decompress(decode_base64_url_safe(data))


def decode_save_apply_xor(data: bytes, key: Key = Key.SAVE) -> bytes:
    """Same as [`decode_save`][gd.crypto.saves.decode_save], but calls
    [`apply_xor`][gd.crypto.saves.apply_xor] with `key` before decoding.

    This function is the inverse of
    [`encode_save_apply_xor`][gd.crypto.saves.encode_save_apply_xor],
    meaning that

    ```python
    decode_save_apply_xor(encode_save_apply_xor(data, key), key) == data
    ```

    holds for any `data` and `key`.

    Arguments:
        data: The data to decode.
        key: The key to use.

    Returns:
        The decoded data.
    """
    return decode_save(apply_xor(data, key))
