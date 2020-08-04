from base64 import urlsafe_b64decode, urlsafe_b64encode
import gzip
import hashlib
import random
import string
import zlib

# absolute import because we are deep
from gd.logging import get_logger
from gd.typing import List, Union

from gd.utils.crypto.xor_cipher import XORCipher as XOR

log = get_logger(__name__)

Z_GZIP_HEADER = 0x10
Z_AUTO_HEADER = 0x20

try:
    from Crypto.Cipher import AES
except ImportError:
    log.warning("Failed to import pycryptodome module. MacOS save coding will not be supported.")


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

    mac_key = (
        b"\x69\x70\x75\x39\x54\x55\x76\x35\x34\x79\x76\x5d\x69\x73\x46\x4d"
        b"\x68\x35\x40\x3b\x74\x2e\x35\x77\x33\x34\x45\x32\x52\x79\x40\x7b"
    )

    try:
        cipher = AES.new(mac_key, AES.MODE_ECB)
    except NameError:  # AES not imported
        pass

    @staticmethod
    def byte_xor(stream: bytes, key: int) -> str:
        return bytes(byte ^ key for byte in stream).decode(errors="ignore")

    @classmethod
    def decode_save(cls, save: Union[bytes, str], needs_xor: bool = True) -> str:
        if isinstance(save, str):
            save = save.encode()

        if needs_xor:
            save = cls.byte_xor(save, 11)

        else:
            save = save.decode()

        remain = len(save) % 4

        if remain:
            save += "=" * (4 - remain)

        return inflate(urlsafe_b64decode(save.encode())).decode(errors="ignore")

    @classmethod
    def decode_mac_save(cls, save: Union[bytes, str], *args, **kwargs) -> str:
        if isinstance(save, str):
            save = save.encode()

        data = cls.cipher.decrypt(save)

        last = data[-1]
        if last < 16:
            data = data[:-last]

        return data.decode(errors="ignore")

    @classmethod
    def encode_mac_save(cls, save: Union[bytes, str], *args, **kwargs) -> bytes:
        if isinstance(save, str):
            save = save.encode()

        remain = len(save) % 16
        if remain:
            to_add = 16 - remain
            save += bytes([to_add] * to_add)

        return cls.cipher.encrypt(save)

    @classmethod
    def encode_save(cls, save: Union[bytes, str], needs_xor: bool = True) -> str:
        if isinstance(save, str):
            save = save.encode()

        final = urlsafe_b64encode(deflate(save))

        if needs_xor:
            final = cls.byte_xor(final, 11)
        else:
            final = final.decode()

        return final

    @classmethod
    def do_base64(
        cls, data: str, encode: bool = True, errors: str = "strict", safe: bool = True
    ) -> str:
        try:
            if encode:
                return urlsafe_b64encode(data.encode(errors=errors)).decode(errors=errors)
            else:
                remain = len(data) % 4

                if remain:
                    data += "=" * (4 - remain)
                return urlsafe_b64decode(data.encode(errors=errors)).decode(errors=errors)

        except Exception:
            if safe:
                return data
            raise

    @classmethod
    def gen_rs(cls, length: int = 10, charset: str = string.ascii_letters + string.digits) -> str:
        """Generates a random string of required length.

        Parameters
        ----------
        length: :class:`int`
            Amount of characters for a string to have.

        charset: :class:`str`
            Character set to use. ``[A-Za-z0-9]`` by default.

        Returns
        -------
        :class:`str`
            Generated string.
        """
        return "".join(random.choices(charset, k=length))

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
    def decode(cls, type: str, string: str, use_bytes: bool = False) -> str:
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
        string += "=" * (4 - len(string) % 4)  # add padding

        try:
            cipher_stream = urlsafe_b64decode(string.encode())
        except Exception:
            return string

        if use_bytes:
            return XOR.cipher_bytes(key=cls.keys[type], stream=cipher_stream)
        else:
            return XOR.cipher(key=cls.keys[type], string=cipher_stream.decode(errors="ignore"))

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
        """Decompresses a level string.

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

        unzipped = inflate(urlsafe_b64decode(string))

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


def deflate(data: bytes) -> bytes:
    compressor = zlib.compressobj(wbits=zlib.MAX_WBITS | Z_GZIP_HEADER)
    data = compressor.compress(data) + compressor.flush()

    return data


def inflate(data: bytes) -> bytes:
    try:
        return gzip.decompress(data)
    except (gzip.BadGzipFile, zlib.error):
        pass

    # fallback and do some other attempts
    for wbits in (zlib.MAX_WBITS | Z_AUTO_HEADER, zlib.MAX_WBITS | Z_GZIP_HEADER, zlib.MAX_WBITS):
        try:
            decompressor = zlib.decompressobj(wbits=wbits)
            data = decompressor.decompress(data) + decompressor.flush()
            return data

        except zlib.error:
            pass

    raise RuntimeError("Failed to decompress data.")
