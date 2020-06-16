from itertools import cycle

from gd.typing import Union


class XORCipher:
    @staticmethod
    def cipher(key: Union[bytes, int, str], string: str) -> str:
        """Ciphers a string with XOR using key given.

        Due to the fact that *XOR* ``^`` operation is being used,
        the following is true:

        .. code-block:: python3

            xor = XORCipher
            xor.cipher('93582', xor.cipher('93582', 'NeKit')) == 'NeKit'  # True

        Parameters
        ----------
        key: Union[:class:`bytes`, :class:`int`, :class:`str`]
            A key to XOR cipher with, e.g. ``'59361'``.

        string: :class:`str`
            A string to apply XOR on.

        Returns
        -------
        :class:`str`
            A string after XOR operation.
        """
        return ("").join(chr(ord(x) ^ ord(y)) for x, y in zip(string, cycle(key_to_string(key))))

    @staticmethod
    def cipher_bytes(key: Union[bytes, int, str], stream: bytes) -> str:
        return ("").join(chr(x ^ ord(y)) for x, y in zip(stream, cycle(key_to_string(key))))


def key_to_string(key: Union[bytes, int, str]) -> str:
    if isinstance(key, str):
        return key
    elif isinstance(key, bytes):
        return key.decode()
    else:
        return str(key)
