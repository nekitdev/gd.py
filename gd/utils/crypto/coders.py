import base64
import hashlib
import random
import string
import struct
import zlib

from typing import Sequence, Union

from ..mapper import mapper_util
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

    @classmethod
    def normal_xor(cls, data: bytes, key: int):
        """Applies simple XOR on an array of bytes.

        Parameters
        ----------
        data: :class:`bytes`
            Data to apply XOR on.

        key: :class:`int`
            A key to XOR data with.

        Returns
        -------
        :class:`str`
            Decoded data as a string.
        """
        return bytearray(i^key for i in data).decode()

    @classmethod
    def decode_save(cls, save: bytes, needs_xor: bool = True):
        if needs_xor:
            save = cls.normal_xor(save, 11)
        elif isinstance(save, bytes):
            save = save.decode(errors='ignore')

        data = mapper_util.normalize(save).encode()

        from_b64 = base64.b64decode(data)[10:]

        return zlib.decompress(from_b64, -zlib.MAX_WBITS)

    @classmethod
    def encode_save(cls, save: bytes, needs_xor: bool = True):
        compressed = zlib.compress(save)

        crc32 = struct.pack('I', zlib.crc32(save))
        save_size = struct.pack('I', len(save))

        encrypted = bytes(cls.additional) + compressed[2:-4] + crc32 + save_size

        encoded = mapper_util.prepare_sending(base64.b64encode(encrypted).decode()).encode()

        return encoded if not needs_xor else cls.normal_xor(encoded, 11).encode()

    @classmethod
    def do_base64(cls, data: str, encode: bool = True):
        if encode:
            return mapper_util.prepare_sending(base64.b64encode(data.encode()).decode())
        else:
            return mapper_util.normalize(base64.b64decode(data.encode()).decode())

    @classmethod
    def gen_rs(cls, length: int = 10):
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
        rand = random.choices(sset, k=length)
        final = ''.join(rand)
        return final

    @classmethod
    def encode(cls, type: str, string: str):
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
        encoded = base64.b64encode(ciphered.encode()).decode()
        return encoded

    @classmethod
    def decode(cls, type: str, string: str):
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
        ciphered = base64.b64decode(string).decode()
        decoded = XOR.cipher(key=cls.keys[type], string=ciphered)
        return decoded

    @classmethod
    def gen_chk(cls, type: str, values: Sequence[Union[int, str]]):
        """Generates a "chk" value, used in different requests to GD servers.

        The method is: combine_values -> add salt -> sha1 hash
        -> XOR -> Base64 encode -> return

        Parameters
        ----------
        type: :class:`str`
            String representation of type, e.g. ``'comment'``.
            Used to define salt and XOR key.

        values: Sequence[Union[:class:`int`, :class:`str`]]
            Sequence of values to generate a chk with.

        Returns
        -------
        :class:`str`
            Generated ``'chk'``, represented as string.
        """
        values = list(map(str, values))
        salt = cls.salts.get(type, '')  # get salt
        string = ''
        # combine
        # special case for 'levelscore'
        if (type == 'levelscore'):
            for i in range(len(values)-1):
                string += values[i]
                if (i == 7):
                    string += '1'
            string += salt + values[-1]
        # normal case
        else:
            for value in values:
                string += value
            string += salt
        # sha1 hash
        hashed = hashlib.sha1(string.encode()).hexdigest()
        # XOR
        xored = XOR.cipher(key=cls.keys[type], string=hashed)
        # Base64
        final = base64.b64encode(xored.encode()).decode()
        return final

    @classmethod
    def unzip(cls, string: str):
        """zlib decompresses a level string.

        Used to unzip level data.

        Parameters
        ----------
        string: :class:`str`
            String to unzip, encoded in Base64.

        Returns
        -------
        :class:`str`
            Unzipped level data, as string.
        """
        decoded = base64.b64decode(mapper_util.normalize(string).encode())

        try:
            unzipped = zlib.decompress(decoded, zlib.MAX_WBITS)
        except zlib.error:
            unzipped = zlib.decompress(decoded[10:], -zlib.MAX_WBITS)

        final = unzipped.decode(errors='ignore').rstrip(';')

        return final

    @classmethod
    def zip(cls, string: str, append_semicolon: bool = True):
        if append_semicolon and not string.endswith(';'):
            string += ';'

        return cls.encode_save(string.encode(), needs_xor=False).decode()

    @classmethod
    def gen_level_upload_seed(cls, data_string: str, chars_required: int = 50):
        if len(data_string) < 50:
            return data_string

        space = len(data_string) // chars_required

        return data_string[::space][:chars_required]

    @classmethod
    def gen_level_lb_seed(cls, jumps: int = 0, percentage: int = 0, seconds: int = 0):
        return 1482 + (jumps + 3991) * (percentage + 8354) + ((seconds + 4085)**2) - 50028039
