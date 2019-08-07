import base64
import gzip
import hashlib

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
            The following is true:

            .. code-block:: python3

                Coder.decode(Coder.encode('NeKit')) == 'NeKit'  # True

        Parameters
        ----------
        type: :class:`str`
            String representation of type, e.g. ``'level'``.
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
            Generated "chk", represented as string.
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
        """Gzip decompresses a string.

        Used to unzip level data.

        Parameters
        ----------
        string: :class:`str`
            String to unzip, encoded in Base64.

        Returns
        -------
        :class:`bytes`
            Unzipped level data, as bytes.
        """
        # TODO: LEVEL DATA UNION -> 1.0 == 1.5 == 2.1
        decoded = base64.b64decode(mapper_util.normalize(string).encode())
        try:
            unzipped = gzip.decompress(decoded)
        except OSError:  # failed to unzip (for older game versions)
            unzipped = decoded
        return unzipped

    @classmethod
    def zip(cls, bytes: bytes):
        """Gzip compresses bytes.

        Used to compress level data.

        Parameters
        ----------
        bytes: :class:`bytes`
            Bytes to zip.

        Returns
        -------
        :class:`str`
            Zipped string, encoded in Base64
        """
        zipped = gzip.compress(bytes)
        encoded = mappet_util.prepare_sending(base64.b64encode(zipped).decode())
        return encoded

    @classmethod
    def gen_level_lb_seed(cls, jumps: int, percentage: int, seconds: int):
        res = 1482 + (jumps + 3991) * (percentage + 8354) + ((seconds + 4085)**2) - 50028039
        return res
