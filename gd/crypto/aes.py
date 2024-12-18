from typing import Literal

__all__ = (
    "AES_KEY",
    "AES_PAD",
    "CIPHER",
    "append_padding",
    "remove_padding",
    "encrypt_aes",
    "decrypt_aes",
)

AES_KEY = b"ipu9TUv54yv]isFMh5@;t.5w34E2Ry@{"
"""The AES key used in Geometry Dash."""

AES_PAD: Literal[16] = 16
"""The padding required in AES."""

try:
    from cryptography.hazmat.primitives.ciphers import Cipher
    from cryptography.hazmat.primitives.ciphers.algorithms import AES
    from cryptography.hazmat.primitives.ciphers.modes import ECB

    CIPHER = Cipher(AES(AES_KEY), ECB())
    """The cipher used in Geometry Dash: AES in ECB mode."""

except ImportError:
    CIPHER = None  # type: ignore[assignment]


LAST = ~0


def last(data: bytes) -> int:
    return data[LAST]


def drop_last(count: int, data: bytes) -> bytes:
    return data[:-count]


def append_padding(data: bytes, pad: int = AES_PAD) -> bytes:
    """Appends padding to the given data.

    Note:
        The method is known as *PKCS padding*.
        This function appends bytes with the value equal to the amount of bytes required.
        For instance, if `7` bytes are required, the padding is `07 07 07 07 07 07 07`.
        The data is *always* padded.

    Arguments:
        data: The data to pad.
        pad: The padding required.

    Returns:
        The padded data.
    """
    byte = pad - len(data) % pad
    padding = bytes([byte] * byte)

    return data + padding


def remove_padding(data: bytes) -> bytes:
    """Removes padding from the given data.

    Warning:
        It is assumed that the data is padded using the same method as
        [`append_padding`][gd.crypto.aes.append_padding], implying that

        ```python
        remove_padding(append_padding(data)) == data
        ```

        holds for any `data`.

    Arguments:
        data: The data to remove padding from.

    Returns:
        The data without padding.
    """
    return drop_last(last(data), data)


CIPHER_NOT_AVAILABLE = "the cipher is not available"


def encrypt_aes(data: bytes) -> bytes:
    """Encrypts `data` using the [`CIPHER`][gd.crypto.aes.CIPHER].

    Note:
        The data is automatically padded via [`append_padding`][gd.crypto.aes.append_padding].

    Arguments:
        data: The data to encrypt.

    Raises:
        OSError: The cipher is not available.

    Returns:
        The encrypted data.
    """
    cipher = CIPHER

    if cipher is None:
        raise OSError(CIPHER_NOT_AVAILABLE)

    encryptor = cipher.encryptor()

    data = append_padding(data)

    return encryptor.update(data) + encryptor.finalize()


def decrypt_aes(data: bytes) -> bytes:
    """Decrypts `data` using the [`CIPHER`][gd.crypto.aes.CIPHER].

    This function is the inverse of [`encrypt_aes`][gd.crypto.aes.encrypt_aes], meaning that

    ```python
    decrypt_aes(encrypt_aes(data)) == data
    ```

    holds for any `data`.

    Note:
        The padding is automatically removed via [`remove_padding`][gd.crypto.aes.remove_padding].

    Arguments:
        data: The data to decrypt.

    Raises:
        OSError: The cipher is not available.

    Returns:
        The decrypted data.
    """
    cipher = CIPHER

    if cipher is None:
        raise OSError(CIPHER_NOT_AVAILABLE)

    decryptor = cipher.decryptor()

    return remove_padding(decryptor.update(data) + decryptor.finalize())
