class XORCipher:

    @classmethod
    def cipher(cls, key: str, string: str):
        """Ciphers a string with XOR using key given.

        Because of using XOR to cipher, the following is true:

        .. code-block:: python3

            xor = XORCipher
            xor.cipher(xor.cipher('91385', 'NeKit')) == 'NeKit'  # True
        """
        keyB = list(map(ord, key))
        stringB = list(map(ord, string))
        result = ''

        for i in range(len(stringB)):
            key_i = i % len(key)
            result += chr(stringB[i] ^ keyB[key_i])

        return result