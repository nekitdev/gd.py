from base64 import b64decode as standard_decode_base64
from base64 import b64encode as standard_encode_base64
from base64 import urlsafe_b64decode as standard_decode_base64_url_safe
from base64 import urlsafe_b64encode as standard_encode_base64_url_safe
from gzip import decompress as standard_decompress
from hashlib import sha1 as standard_sha1
from random import choices
from random import randrange as random_range
from string import ascii_letters, digits
from typing import AnyStr, Iterable, Sequence, TypeVar
from zlib import MAX_WBITS
from zlib import compressobj as create_compressor
from zlib import decompressobj as create_decompressor
from zlib import error as ZLibError

from xor_cipher import cyclic_xor, cyclic_xor_string, xor, xor_string

from gd.constants import (
    DEFAULT_APPLY_XOR,
    DEFAULT_CHECK,
    DEFAULT_CLICKS,
    DEFAULT_ENCODING,
    DEFAULT_ERRORS,
    DEFAULT_RECORD,
    DEFAULT_SECONDS,
)
from gd.enums import Key, Salt, SimpleKey
from gd.platform import DARWIN
from gd.string_utils import concat_empty

__all__ = (
    "AES_KEY",
    "CIPHER",
    "ECB_PAD",
    "SAVE_KEY",
    "CHARACTERS",
    "enforce_valid_base64",
    "decode_base64",
    "encode_base64",
    "decode_base64_url_safe",
    "encode_base64_url_safe",
    "decode_base64_string",
    "encode_base64_string",
    "decode_base64_string_url_safe",
    "encode_base64_string_url_safe",
    "xor",
    "cyclic_xor",
    "xor_string",
    "cyclic_xor_string",
    "decode_save",
    "encode_save",
    "decode_save_string",
    "encode_save_string",
    "generate_random_string_and_encode_value",
    "generate_random_string",
    "decode_robtop",
    "encode_robtop",
    "decode_robtop_string",
    "encode_robtop_string",
    "decode_darwin_save",
    "encode_darwin_save",
    "decode_system_save",
    "encode_system_save",
    "sha1",
    "sha1_with_salt",
    "sha1_string",
    "sha1_string_with_salt",
    "generate_check",
    "zip_level",
    "unzip_level",
    "zip_level_string",
    "unzip_level_string",
    "generate_level_seed",
    "generate_leaderboard_seed",
    "compress",
    "decompress",
    "fix_song_encoding",
)

# zlib headers

Z_GZIP_HEADER = 0x10
Z_AUTO_HEADER = 0x20

# AES

try:
    from Crypto.Cipher import AES

except ImportError:
    AES = None  # type: ignore

AES_KEY = b"ipu9TUv54yv]isFMh5@;t.5w34E2Ry@{"

CIPHER = None if AES is None else AES.new(AES_KEY, AES.MODE_ECB)

# padding

BASE64_PAD = 4
BASE64_INVALID_TO_PAD = 1
BASE64_PADDING = b"="

ECB_PAD = 16

# save key

SAVE_KEY = SimpleKey.SAVE.value

# characters

CHARACTERS = ascii_letters + digits


LAST = ~0

T = TypeVar("T")


def last(sequence: Sequence[T]) -> T:
    return sequence[LAST]


def drop_last(count: int, data: bytes) -> bytes:
    return data[:-count]


def enforce_valid_base64(data: bytes) -> bytes:
    base64_pad = BASE64_PAD
    base64_padding = BASE64_PADDING
    base64_invalid_to_pad = BASE64_INVALID_TO_PAD

    required = len(data) % base64_pad

    if required:
        if required == base64_invalid_to_pad:
            data = drop_last(base64_invalid_to_pad, data)

        else:
            data += base64_padding * (base64_pad - required)

    return data


def decode_base64(data: bytes) -> bytes:
    return standard_decode_base64(enforce_valid_base64(data))


def encode_base64(data: bytes) -> bytes:
    return standard_encode_base64(data)


def decode_base64_url_safe(data: bytes) -> bytes:
    return standard_decode_base64_url_safe(enforce_valid_base64(data))


def encode_base64_url_safe(data: bytes) -> bytes:
    return standard_encode_base64_url_safe(data)


def decode_base64_string(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return decode_base64(string.encode(encoding, errors)).decode(encoding, errors)


def encode_base64_string(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return encode_base64(string.encode(encoding, errors)).decode(encoding, errors)


def decode_base64_string_url_safe(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return decode_base64_url_safe(string.encode(encoding, errors)).decode(encoding, errors)


def encode_base64_string_url_safe(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return encode_base64_url_safe(string.encode(encoding, errors)).decode(encoding, errors)


def decode_save(data: bytes, apply_xor: bool = DEFAULT_APPLY_XOR) -> bytes:
    if apply_xor:
        data = xor(data, SAVE_KEY)

    return decompress(decode_base64_url_safe(data))


def encode_save(data: bytes, apply_xor: bool = DEFAULT_APPLY_XOR) -> bytes:
    data = encode_base64_url_safe(compress(data))

    if apply_xor:
        data = xor(data, SAVE_KEY)

    return data


def decode_save_string(
    string: str,
    apply_xor: bool = DEFAULT_APPLY_XOR,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    return decode_save(string.encode(encoding, errors), apply_xor).decode(encoding, errors)


def encode_save_string(
    string: str,
    apply_xor: bool = DEFAULT_APPLY_XOR,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    return encode_save(string.encode(encoding, errors), apply_xor).decode(encoding, errors)


DEFAULT_LENGTH_WITH_VALUE = 5
DEFAULT_START = 1000
DEFAULT_STOP = 1000000


def generate_random_string_and_encode_value(
    key: Key,
    length: int = DEFAULT_LENGTH_WITH_VALUE,
    start: int = DEFAULT_START,
    stop: int = DEFAULT_STOP,
    characters: str = CHARACTERS,
) -> str:
    return generate_random_string(length, characters) + encode_robtop_string(
        str(random_range(start, stop)), key
    )


DEFAULT_LENGTH = 10


def generate_random_string(length: int = 10, characters: str = CHARACTERS) -> str:
    return concat_empty(choices(characters, k=length))


def decode_robtop(data: bytes, key: Key) -> bytes:
    return cyclic_xor(decode_base64(data), key.bytes)


def encode_robtop(data: bytes, key: Key) -> bytes:
    return encode_base64(cyclic_xor(data, key.bytes))


def decode_robtop_string(
    string: str, key: Key, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return decode_robtop(string.encode(encoding, errors), key).decode(encoding, errors)


def encode_robtop_string(
    string: str, key: Key, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return encode_robtop(string.encode(encoding, errors), key).decode(encoding, errors)


def decode_darwin_save(
    data: bytes, apply_xor: bool = DEFAULT_APPLY_XOR  # `apply_xor` is here for compatibility
) -> bytes:
    cipher = CIPHER

    if cipher is None:
        raise OSError  # TODO: message?

    data = cipher.decrypt(data)

    data = drop_last(last(data), data)

    return data


def encode_darwin_save(
    data: bytes,
    apply_xor: bool = DEFAULT_APPLY_XOR,  # `apply_xor` is here, again, for compatibility
) -> bytes:
    cipher = CIPHER

    if cipher is None:
        raise OSError  # TODO: message?

    pad = ECB_PAD

    required = len(data) % pad

    byte = pad - required
    data += bytes([byte] * byte)

    return cipher.encrypt(data)


if DARWIN:
    decode_system_save, encode_system_save = decode_darwin_save, encode_darwin_save

else:
    decode_system_save, encode_system_save = decode_save, encode_save


def sha1(data: bytes) -> str:
    return standard_sha1(data).hexdigest()


def sha1_with_salt(stream: bytes, salt: Salt) -> str:
    return standard_sha1(stream + salt.bytes).hexdigest()


def sha1_string(string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS) -> str:
    return sha1(string.encode(encoding, errors))


def sha1_string_with_salt(
    string: str, salt: Salt, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return sha1_with_salt(string.encode(encoding, errors), salt)


def generate_check(
    values: Iterable[str],
    key: Key,
    salt: Salt,
    encoding: str = DEFAULT_ENCODING,
    errors: str = DEFAULT_ERRORS,
) -> str:
    return encode_robtop_string(
        sha1_string_with_salt(concat_empty(values), salt, encoding, errors),
        key,
        encoding,
        errors,
    )


def zip_level(data: bytes) -> bytes:
    return encode_save(data, apply_xor=False)


def unzip_level(data: bytes) -> bytes:
    return decode_save(data, apply_xor=False)


def zip_level_string(
    data: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return encode_save_string(data, apply_xor=False, encoding=encoding, errors=errors)


def unzip_level_string(
    data: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return decode_save_string(data, apply_xor=False, encoding=encoding, errors=errors)


DEFAULT_COUNT = 50


def generate_level_seed(data: AnyStr, count: int = DEFAULT_COUNT) -> AnyStr:
    length = len(data)

    if length < count:
        return data

    return data[:: length // count][:count]


CHECK_MULTIPLY = 1482
ATTEMPTS_ADD = 8354
CLICKS_ADD = 3991
RECORD_ADD = 8354
SECONDS_ADD = 4085
COINS_ADD = 5819

TOTAL_SUBTRACT = CLICKS_ADD * RECORD_ADD + SECONDS_ADD * SECONDS_ADD


def generate_leaderboard_seed(
    clicks: int = DEFAULT_CLICKS,
    record: int = DEFAULT_RECORD,
    seconds: int = DEFAULT_SECONDS,
    check: bool = DEFAULT_CHECK,
) -> int:
    return (
        CHECK_MULTIPLY * check
        + (clicks + CLICKS_ADD) * (record + RECORD_ADD)
        + pow(seconds + SECONDS_ADD, 2)
        - TOTAL_SUBTRACT
    )


def compress(data: bytes) -> bytes:
    compressor = create_compressor(wbits=MAX_WBITS | Z_GZIP_HEADER)

    return compressor.compress(data) + compressor.flush()


def decompress(data: bytes) -> bytes:
    try:
        return standard_decompress(data)

    except (OSError, ZLibError):
        pass

    # fallback and do some other attempts
    for wbits in (
        MAX_WBITS | Z_AUTO_HEADER,
        MAX_WBITS | Z_GZIP_HEADER,
        MAX_WBITS,
    ):
        try:
            decompressor = create_decompressor(wbits=wbits)

            return decompressor.decompress(data) + decompressor.flush()

        except ZLibError:
            pass

    raise RuntimeError("Failed to decompress data.")


LEGACY = "cp1252"
UTF_8 = "utf-8"


def fix_song_encoding(string: str, errors: str = DEFAULT_ERRORS) -> str:
    try:
        return string.encode(LEGACY, errors).decode(UTF_8, errors)

    except (UnicodeEncodeError, UnicodeDecodeError):
        return string
