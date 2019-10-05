class XORCipher:

    @staticmethod
    def cipher(key: str, string: str):
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
        keyB = tuple(map(ord, key))  # we need an index
        stringB = map(ord, string)
        result = ''

        for i, byte in enumerate(stringB):
            key_i = i % len(key)
            result += chr(byte ^ keyB[key_i])

        return result
