from base64 import urlsafe_b64decode, urlsafe_b64encode
import hashlib
import random
import string
import struct
import zlib

try:
    from Crypto.Cipher import AES
except ImportError:
    print("Failed to import pycryptodome module. MacOS save coding will not be supported")

# absolute import because we are deep
from gd.typing import List, Union

from .xor_cipher import XORCipher as XOR


class Coder:
    keys = {
        "message": "14251",
        "levelpass": "26364",
        "accountpass": "37526",
        "levelscore": "39673",
        "level": "41274",
        "comment": "29481",
        "challenges": "19847",
        "rewards": "59182",
        "like_rate": "58281",
        "userscore": "85271",
    }

    salts = {
        "level": "xI25fpAapCQg",
        "comment": "xPT6iUrtws0J",
        "like_rate": "ysg6pUrtjn0J",
        "userscore": "xI35fsAapCRg",
        "levelscore": "yPg6pUrtWn0J",
    }

    additional = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x0b"
    base64_additional = urlsafe_b64encode(additional).decode().rstrip("=")

    mac_key = (
        b"\x69\x70\x75\x39\x54\x55\x76\x35\x34\x79\x76\x5d\x69\x73\x46\x4d"
        b"\x68\x35\x40\x3b\x74\x2e\x35\x77\x33\x34\x45\x32\x52\x79\x40\x7b"
    )

    try:
        cipher = AES.new(mac_key, AES.MODE_ECB)
    except NameError:  # AES not imported
        pass

    @staticmethod
    def normal_xor(string: str, key: int) -> str:
        return "".join(chr(ord(char) ^ key) for char in string)

    @classmethod
    def decode_save(cls, save: str, needs_xor: bool = True) -> str:
        if needs_xor:
            save = cls.normal_xor(save, 11)

        save += "=" * (4 - len(save) % 4)

        return pako_inflate(urlsafe_b64decode(save.encode())).decode(errors="replace")

    @classmethod
    def decode_mac_save(cls, save: Union[bytes, str], *args, **kwargs) -> bytes:
        if isinstance(save, str):
            save = save.encode()

        data = cls.cipher.decrypt(save)

        last = data[-1]
        if last < 16:
            data = data[:-last]

        return data.decode()

    @classmethod
    def encode_mac_save(cls, save: Union[bytes, str], *args, **kwargs) -> bytes:
        if isinstance(save, str):
            save = save.encode()

        remain = len(save) % 16
        if remain:
            to_add = 16 - remain
            save += to_add.to_bytes(1, "little") * to_add

        return cls.cipher.encrypt(save)

    @classmethod
    def encode_save(cls, save: Union[bytes, str], needs_xor: bool = True) -> str:
        if isinstance(save, str):
            save = save.encode()

        compressed = pako_deflate(save)

        crc32 = struct.pack("I", zlib.crc32(save))
        save_size = struct.pack("I", len(save))

        encrypted = cls.additional + compressed[2:-4] + crc32 + save_size

        final = urlsafe_b64encode(encrypted).decode()

        if needs_xor:
            final = cls.normal_xor(final, 11)

        return final

    @classmethod
    def do_base64(cls, data: str, encode: bool = True, errors: str = "strict") -> str:
        try:
            if encode:
                return urlsafe_b64encode(data.encode(errors=errors)).decode(errors=errors)
            else:
                padded = data + ("=" * (4 - len(data) % 4))
                return urlsafe_b64decode(padded.encode(errors=errors)).decode(errors=errors)

        except Exception:
            return data

    @classmethod
    def gen_rs(cls, length: int = 10) -> str:
        """Generates a random string of required length.

        Uses [A-Za-z0-9] character set.

        Parameters
        ----------
        length: :class:`int`
            Amount of characters for a string to have.

        Returns
        -------
        :class:`str`
            Generated string.
        """
        sset = string.ascii_letters + string.digits
        return "".join(random.choice(sset) for _ in range(length))

    @classmethod
    def encode(cls, type: str, string: str) -> str:
        """Encodes a string, combining XOR and Base64 encode methods.

        Used in different aspects of gd.py.

        Parameters
        ----------
        type: :class:`str`
            String representation of type, e.g. ``'levelpass'``.
            Used to define a XOR key.

        string: :class:`str`
            String to encode.

        Returns
        -------
        :class:`str`
            Encoded string.
        """
        ciphered = XOR.cipher(key=cls.keys[type], string=string)
        encoded = cls.do_base64(ciphered, encode=True)
        return encoded

    @classmethod
    def decode(cls, type: str, string: str) -> str:
        """Decodes a XOR -> Base64 ciphered string.

        .. note::
            Due to the fact that decode and encode work almost the same,
            the following is true:

            .. code-block:: python3

                Coder.decode('message', Coder.encode('message', 'NeKit')) == 'NeKit'  # True

        Parameters
        ----------
        type: :class:`str`
            String representation of a type, e.g. ``'level'``.
            Used to define a XOR key.

        string: :class:`str`
            String to decode.

        Returns
        -------
        :class:`str`
            Decoded string.
        """
        ciphered = cls.do_base64(string, encode=False)
        decoded = XOR.cipher(key=cls.keys[type], string=ciphered)
        return decoded

    @classmethod
    def gen_chk(cls, type: str, values: List[Union[int, str]]) -> str:
        """Generates a "chk" value, used in different requests to GD servers.

        The method is: combine_values -> add salt -> sha1 hash
        -> XOR -> Base64 encode -> return

        Parameters
        ----------
        type: :class:`str`
            String representation of type, e.g. ``'comment'``.
            Used to define salt and XOR key.

        values: List[Union[:class:`int`, :class:`str`]]
            List of values to generate a chk with.

        Returns
        -------
        :class:`str`
            Generated ``'chk'``, represented as string.
        """
        salt = cls.salts.get(type, "")  # get salt

        values.append(salt)

        string = "".join(map(str, values))

        # sha1 hash
        hashed = hashlib.sha1(string.encode()).hexdigest()
        # XOR
        xored = XOR.cipher(key=cls.keys[type], string=hashed)
        # Base64
        final = cls.do_base64(xored, encode=True)

        return final

    @classmethod
    def unzip(cls, string: Union[bytes, str]) -> Union[bytes, str]:
        """zlib decompresses a level string.

        Used to unzip level data.

        Parameters
        ----------
        string: Union[:class:`bytes`, :class:`str`]
            String to unzip, encoded in Base64.

        Returns
        -------
        Union[:class:`bytes`, :class:`str`]
            Unzipped level data, as a stream.
        """
        if isinstance(string, str):
            string = string.encode()

        decoded = urlsafe_b64decode(string)

        unzipped = pako_inflate(decoded)

        try:
            final = unzipped.decode()
        except UnicodeDecodeError:
            final = unzipped

        return final

    @classmethod
    def zip(cls, string: Union[bytes, str], append_semicolon: bool = True) -> str:
        if isinstance(string, bytes):
            string = string.decode(errors="ignore")

        if append_semicolon and not string.endswith(";"):
            string += ";"

        return cls.encode_save(string, needs_xor=False)

    @classmethod
    def gen_level_upload_seed(cls, data_string: str, chars_required: int = 50) -> str:
        if len(data_string) < chars_required:
            return data_string

        space = len(data_string) // chars_required

        return data_string[::space][:chars_required]

    @classmethod
    def gen_level_lb_seed(
        cls, jumps: int = 0, percentage: int = 0, seconds: int = 0, played: bool = True
    ) -> int:
        return (
            1482 * (played + 1)
            + (jumps + 3991) * (percentage + 8354)
            + ((seconds + 4085) ** 2)
            - 50028039
        )


def pako_inflate(data: bytes) -> bytes:
    decompress = zlib.decompressobj(15 | 32)
    decompressed = decompress.decompress(data) + decompress.flush()
    return decompressed


def pako_deflate(data: bytes) -> bytes:
    compress = zlib.compressobj(
        zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, 15, memLevel=8, strategy=zlib.Z_DEFAULT_STRATEGY
    )
    compressed = compress.compress(data) + compress.flush()
    return compressed
