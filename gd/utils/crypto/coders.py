import base64
import hashlib
import random
import string
import struct
import zlib

# absolute import because we are deep
from gd.typing import List, Union

from .xor_cipher import XORCipher as XOR


class Coder:
    keys = {
        'message': '14251',
        'levelpass': '26364',
        'accountpass': '37526',
        'levelscore': '39673',
        'level': '41274',
        'comment': '29481',
        'challenges': '19847',
        'rewards': '59182',
        'like_rate': '58281',
        'userscore': '85271'
    }

    salts = {
        'level': 'xI25fpAapCQg',
        'comment': 'xPT6iUrtws0J',
        'like_rate': 'ysg6pUrtjn0J',
        'userscore': 'xI35fsAapCRg',
        'levelscore': 'yPg6pUrtWn0J'
    }

    additional = (0x1f, 0x8b, 0x8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xb)

    @staticmethod
    def normal_xor(string: str, key: int) -> str:
        return str().join(chr(ord(char) ^ key) for char in string)

    @classmethod
    def decode_save(cls, save: str, needs_xor: bool = True) -> str:
        if needs_xor:
            save = cls.normal_xor(save, 11)

        return zlib.decompress(
            base64.urlsafe_b64decode(save.encode()), zlib.MAX_WBITS | 0x10
        ).decode(errors='replace')

    @classmethod
    def encode_save(cls, save: Union[bytes, str], needs_xor: bool = True) -> str:
        if isinstance(save, str):
            save = save.encode()

        compressed = zlib.compress(save)

        crc32 = struct.pack('I', zlib.crc32(save))
        save_size = struct.pack('I', len(save))

        encrypted = bytes(cls.additional) + compressed[2:-4] + crc32 + save_size

        final = base64.urlsafe_b64encode(encrypted).decode()

        if needs_xor:
            final = cls.normal_xor(final, 11)

        return final

    @classmethod
    def do_base64(cls, data: str, encode: bool = True, errors: str = 'strict') -> str:
        try:
            if encode:
                return base64.urlsafe_b64encode(
                    data.encode(errors=errors)
                ).decode(errors=errors)
            else:
                padded = data + ('=' * (len(data) % 4))
                return base64.urlsafe_b64decode(
                    padded.encode(errors=errors)
                ).decode(errors=errors)

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
        return str().join(random.choice(sset) for _ in range(length))

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
        encoded = base64.urlsafe_b64encode(ciphered.encode()).decode()
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
        ciphered = base64.urlsafe_b64decode(string).decode()
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
        salt = cls.salts.get(type, '')  # get salt

        if (type == 'levelscore'):
            values.insert(8, 1)
            values.insert(-1, salt)

        else:
            values.append(salt)

        string = str().join(map(str, values))

        # sha1 hash
        hashed = hashlib.sha1(string.encode()).hexdigest()
        # XOR
        xored = XOR.cipher(key=cls.keys[type], string=hashed)
        # Base64
        final = base64.urlsafe_b64encode(xored.encode()).decode()
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

        decoded = base64.urlsafe_b64decode(string)

        try:
            unzipped = zlib.decompress(decoded, zlib.MAX_WBITS | 0x10)
        except zlib.error:
            unzipped = zlib.decompress(decoded, zlib.MAX_WBITS)

        try:
            final = unzipped.decode()
        except UnicodeDecodeError:
            final = unzipped

        return final

    @classmethod
    def zip(cls, string: Union[bytes, str], append_semicolon: bool = True) -> str:
        if isinstance(string, bytes):
            string = string.decode(errors='ignore')

        if append_semicolon and not string.endswith(';'):
            string += ';'

        return cls.encode_save(string, needs_xor=False)

    @classmethod
    def gen_level_upload_seed(cls, data_string: str, chars_required: int = 50) -> str:
        if len(data_string) < 50:
            return data_string

        space = len(data_string) // chars_required

        return data_string[::space][:chars_required]

    @classmethod
    def gen_level_lb_seed(cls, jumps: int = 0, percentage: int = 0, seconds: int = 0) -> int:
        return (
            1482 + (jumps + 3991) * (percentage + 8354) + ((seconds + 4085)**2) - 50028039
        )
