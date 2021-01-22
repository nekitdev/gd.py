import gzip
import hashlib
import random
import string
import zlib
from base64 import b64decode, b64encode, urlsafe_b64decode, urlsafe_b64encode
from itertools import cycle

from gd.enums import Key, Salt
from gd.logging import get_logger
from gd.platform import MACOS
from gd.text_utils import concat
from gd.typing import AnyStr, List, TypeVar

__all__ = (
    "AES_KEY",
    "CHARSET",
    "DEFAULT_ENCODING",
    "DEFAULT_ERRORS",
    "XOR_KEY",
    "Key",
    "Salt",
    "decode_base64",
    "encode_base64",
    "decode_base64_str",
    "encode_base64_str",
    "xor",
    "cyclic_xor",
    "xor_str",
    "cyclic_xor_str",
    "decode_mac_save",
    "encode_mac_save",
    "decode_save",
    "encode_save",
    "decode_save_str",
    "encode_save_str",
    "decode_os_save",
    "encode_os_save",
    "sha1",
    "sha1_str",
    "sha1_with_salt",
    "sha1_str_with_salt",
    "zip_level",
    "unzip_level",
    "zip_level_str",
    "unzip_level_str",
    "gen_chk",
    "gen_rs",
    "gen_rs_and_encode_number",
    "gen_level_seed",
    "gen_leaderboard_seed",
    "deflate",
    "inflate",
    "fix_song_encoding",
)

log = get_logger(__name__)

T = TypeVar("T")

# zlib headers

Z_GZIP_HEADER = 0x10
Z_AUTO_HEADER = 0x20

# AES cipher

try:
    from Crypto.Cipher import AES
except ImportError:
    log.warning("Failed to import pycryptodome module. MacOS save coding will not be supported.")

AES_KEY = (
    b"\x69\x70\x75\x39\x54\x55\x76\x35\x34\x79\x76\x5d\x69\x73\x46\x4d"
    b"\x68\x35\x40\x3b\x74\x2e\x35\x77\x33\x34\x45\x32\x52\x79\x40\x7b"
)

try:
    CIPHER = AES.new(AES_KEY, AES.MODE_ECB)
except NameError:
    pass

# padding

BASE64_PAD = 4
BASE64_INVALID_TO_PAD = 1
ECB_PAD = 16
PADDING = b"="

# encoding

DEFAULT_ENCODING = "utf-8"
DEFAULT_ERRORS = "strict"

# save key

XOR_KEY = 11

# charset and concat

CHARSET = string.ascii_letters + string.digits


def decode_base64(data: bytes, urlsafe: bool = True) -> bytes:
    """Decode Base64, correctly padding the data.

    Parameters
    ----------
    data: :class:`bytes`
        Stream to decode Base64 from.

    urlsafe: :class:`bool`
        Whether to use URL-safe decoding.

    Returns
    -------
    :class:`bytes`
        Decoded data.
    """
    required = len(data) % BASE64_PAD

    if required:  # handle padding
        if required != BASE64_INVALID_TO_PAD:
            data += PADDING * (BASE64_PAD - required)

        else:  # 1 more than a multiple of 4, strip last byte
            data = data[:-1]

    if urlsafe:
        return urlsafe_b64decode(data)

    return b64decode(data)


def encode_base64(data: bytes, urlsafe: bool = True) -> bytes:
    """Encode Base64, correctly padding the data.

    Parameters
    ----------
    data: :class:`bytes`
        Stream to encode Base64 from.

    urlsafe: :class:`bool`
        Whether to use URL-safe encode.

    Returns
    -------
    :class:`bytes`
        Encoded data.
    """
    if urlsafe:
        return urlsafe_b64encode(data)

    return b64encode(data)


def decode_base64_str(
    string: str,
    urlsafe: bool = True,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """Decode Base64, correctly padding the string.

    This is similar to :func:`~gd.crypto.decode_base64`,
    except it operates on strings with their encoding.

    Parameters
    ----------
    string: :class:`str`
        String to decode Base64 from.

    urlsafe: :class:`bool`
        Whether to use URL-safe decoding.

    encoding: :class:`str`
        Encoding to use, ``utf-8`` by default.

    errors: :class:`str`
        Errors handling to use, ``strict`` by default.

    Returns
    -------
    :class:`str`
        Decoded string.
    """
    return decode_base64(string.encode(encoding, errors), urlsafe).decode(encoding, errors)


def encode_base64_str(
    string: str,
    urlsafe: bool = True,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    """Encode Base64, correctly padding the string.

    This is similar to :func:`~gd.crypto.encode_base64`,
    except it operates on strings with their encoding.

    Parameters
    ----------
    string: :class:`str`
        String to encode Base64 from.

    urlsafe: :class:`bool`
        Whether to use URL-safe encoding.

    encoding: :class:`str`
        Encoding to use, ``utf-8`` by default.

    errors: :class:`str`
        Errors handling to use, ``strict`` by default.

    Returns
    -------
    :class:`str`
        Encoded string.
    """
    return encode_base64(string.encode(encoding, errors), urlsafe).decode(encoding, errors)


def xor(stream: bytes, key: int) -> bytes:
    """Apply XOR cipher to ``stream`` with ``key``.
    Applying this operation twice decodes ``stream`` back to the initial state.

    Parameters
    ----------
    stream: :class:`bytes`
        Data to apply XOR on.

    key: :class:`int`
        Key to use. Type ``u8`` (or ``byte``) should be used, in ``[0; 255]`` range.

    Returns
    -------
    :class:`bytes`
        Data after XOR applied.
    """
    return bytes(byte ^ key for byte in stream)


def cyclic_xor(stream: bytes, key: bytes) -> bytes:
    """Apply cyclic XOR cipher to ``stream`` with ``key``.
    Applying this operation twice decodes ``stream`` back to the initial state.

    Parameters
    ----------
    stream: :class:`bytes`
        Data to apply XOR on.

    key: :class:`bytes`
        Key to use. It is cycled and zipped with ``stream``.

    Returns
    -------
    :class:`bytes`
        Data after XOR applied.
    """
    return bytes(byte ^ key_byte for (byte, key_byte) in zip(stream, cycle(key)))


def xor_str(
    string: str, key: int, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS,
) -> str:
    """Apply XOR cipher to ``string`` with ``key``.
    Applying this operation twice decodes ``string`` back to the initial state.

    Parameters
    ----------
    string: :class:`str`
        String to apply XOR on.

    key: :class:`int`
        Key to use. Type ``u8`` (or ``byte``) should be used, in ``[0; 255]`` range.

    Returns
    -------
    :class:`str`
        String after XOR applied.
    """
    return xor(string.encode(encoding, errors), key).decode(encoding, errors)


def cyclic_xor_str(
    string: str, key: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS,
) -> str:
    """Apply cyclic XOR cipher to ``string`` with ``key``.
    Applying this operation twice decodes ``string`` back to the initial state.

    Parameters
    ----------
    string: :class:`str`
        String to apply XOR on.

    key: :class:`str`
        Key to use. It is cycled and zipped with ``string``.

    Returns
    -------
    :class:`str`
        String after XOR applied.
    """
    return cyclic_xor(string.encode(encoding, errors), key.encode(encoding, errors)).decode(
        encoding, errors
    )


def decode_save(save_data: bytes, apply_xor: bool = True) -> bytes:
    if apply_xor:
        save_data = xor(save_data, XOR_KEY)

    return inflate(decode_base64(save_data))


def encode_save(save_data: bytes, apply_xor: bool = True) -> bytes:
    save_data = encode_base64(deflate(save_data))

    if apply_xor:
        save_data = xor(save_data, XOR_KEY)

    return save_data


def decode_save_str(
    string: str,
    apply_xor: bool = True,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    return decode_save(string.encode(encoding, errors), apply_xor).decode(encoding, errors)


def encode_save_str(
    string: str,
    apply_xor: bool = True,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    return encode_save(string.encode(encoding, errors), apply_xor).decode(encoding, errors)


def gen_rs_and_encode_number(
    length: int = 5, start: int = 1_000, stop: int = 1_000_000, *, key: Key,
) -> str:
    return gen_rs(length) + encode_robtop_str(str(random.randrange(start, stop)), key)


def gen_rs(length: int = 10, charset: str = CHARSET) -> str:
    return concat(random.choices(charset, k=length))


def decode_robtop(data: bytes, key: Key) -> bytes:
    return cyclic_xor(decode_base64(data), key.bytes)


def encode_robtop(data: bytes, key: Key) -> bytes:
    return encode_base64(cyclic_xor(data, key.bytes))


def decode_robtop_str(
    string: str, key: Key, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS,
) -> str:
    return decode_robtop(string.encode(encoding, errors), key).decode(encoding, errors)


def encode_robtop_str(
    string: str, key: Key, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS,
) -> str:
    return encode_robtop(string.encode(encoding, errors), key).decode(encoding, errors)


def decode_mac_save(
    save_data: bytes, apply_xor: bool = True  # apply_xor is here for compatibility
) -> bytes:
    save_data = CIPHER.decrypt(save_data)

    pad = save_data[-1]

    if pad < ECB_PAD:
        save_data = save_data[:-pad]

    return save_data


def encode_mac_save(
    save_data: bytes, apply_xor: bool = True,  # apply_xor is here, again, for compatibility
) -> bytes:
    required = len(save_data) % ECB_PAD

    if required:
        byte = ECB_PAD - required
        save_data += bytes([byte] * byte)

    return CIPHER.encrypt(save_data)


if MACOS:
    decode_os_save, encode_os_save = decode_mac_save, encode_mac_save

else:
    decode_os_save, encode_os_save = decode_save, encode_save


def sha1(stream: bytes) -> str:
    return hashlib.sha1(stream).hexdigest()


def sha1_with_salt(stream: bytes, salt: Salt) -> str:
    return hashlib.sha1(stream + salt.bytes).hexdigest()


def sha1_str(string: str) -> str:
    return hashlib.sha1(string.encode(DEFAULT_ENCODING, DEFAULT_ERRORS)).hexdigest()


def sha1_str_with_salt(string: str, salt: Salt) -> str:
    return hashlib.sha1((string + salt.string).encode(DEFAULT_ENCODING, DEFAULT_ERRORS)).hexdigest()


def decode_bytes_else_str(value: T) -> str:
    if isinstance(value, bytes):
        return value.decode(DEFAULT_ENCODING, DEFAULT_ERRORS)

    return str(value)


def gen_chk(values: List[T], key: Key, salt: Salt) -> str:
    string = concat(map(decode_bytes_else_str, values))

    return encode_robtop_str(sha1_str_with_salt(string, salt), key)


def zip_level(level_data: bytes) -> bytes:
    return encode_save(level_data, apply_xor=False)


def unzip_level(level_data: bytes) -> bytes:
    return decode_save(level_data, apply_xor=False)


def zip_level_str(
    level_data: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return encode_save_str(level_data, apply_xor=False, encoding=encoding, errors=errors)


def unzip_level_str(
    level_data: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return decode_save_str(level_data, apply_xor=False, encoding=encoding, errors=errors)


def gen_level_seed(level_data: AnyStr, chars: int = 50) -> AnyStr:
    if len(level_data) < chars:
        return level_data

    return level_data[:: len(level_data) // chars][:chars]


def gen_leaderboard_seed(
    cls, jumps: int = 0, percentage: int = 0, seconds: int = 0, has_played: bool = True
) -> int:
    return (
        1482 * (has_played + 1)
        + (jumps + 3991) * (percentage + 8354)
        + ((seconds + 4085) ** 2)
        - 50028039
    )


def deflate(data: bytes) -> bytes:
    compressor = zlib.compressobj(wbits=zlib.MAX_WBITS | Z_GZIP_HEADER)

    return compressor.compress(data) + compressor.flush()


def inflate(data: bytes) -> bytes:
    try:
        return gzip.decompress(data)

    except (OSError, zlib.error):
        pass

    # fallback and do some other attempts
    for wbits in (
        zlib.MAX_WBITS | Z_AUTO_HEADER,
        zlib.MAX_WBITS | Z_GZIP_HEADER,
        zlib.MAX_WBITS,
    ):
        try:
            decompressor = zlib.decompressobj(wbits=wbits)

            return decompressor.decompress(data) + decompressor.flush()

        except zlib.error:
            pass

    raise RuntimeError("Failed to decompress data.")


def fix_song_encoding(string: str) -> str:
    try:
        return string.encode("cp1252").decode("utf-8")

    except (UnicodeEncodeError, UnicodeDecodeError):
        return string


try:
    from _gd import cyclic_xor, xor  # type: ignore  # noqa

except ImportError:
    pass
