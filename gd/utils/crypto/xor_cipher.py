from itertools import cycle


class XORCipher:

    @staticmethod
    def cipher(key: str, string: str) -> str:
        """Ciphers a string with XOR using key given.

        Due to the fact that *XOR* ``^`` operation is being used,
        the following is true:

        .. code-block:: python3

            xor = XORCipher
            xor.cipher('93582', xor.cipher('93582', 'NeKit')) == 'NeKit'  # True

        Parameters
        ----------
        key: :class:`str`
            A key to XOR cipher with, e.g. ``'59361'``.

        string: :class:`str`
            A string to apply XOR on.

        Returns
        -------
        :class:`str`
            A string after XOR operation.
        """
        return ('').join(chr(ord(x) ^ ord(y)) for x, y in zip(string, cycle(key)))
