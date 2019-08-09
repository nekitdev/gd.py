class XORCipher:

    @classmethod
    def cipher(cls, key: str, string: str):
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
        keyB = list(map(ord, key))
        stringB = list(map(ord, string))
        result = ''

        for i in range(len(stringB)):
            key_i = i % len(key)
            result += chr(stringB[i] ^ keyB[key_i])

        return result