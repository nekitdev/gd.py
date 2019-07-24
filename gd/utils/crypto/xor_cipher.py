class XORCipher:
    def cipher(key, string):
        keyB = list(map(ord, key))
        stringB = list(map(ord, string))
        result = ''
        i = 0  # index value
        while i < len(stringB):
            key_i = i % len(key)
            result += chr(stringB[i] ^ keyB[key_i])
            i += 1
        return result