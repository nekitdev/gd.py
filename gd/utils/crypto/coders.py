from .xor_cipher import XORCipher as XOR
import base64

class Coder:

    def __init__(self):
        self.keys = {
            'message': '14251',
            'levelpass': '26364',
            'accountpass': '37526'
        }

    def encode0(self, **kwargs):
        type0 = kwargs.get('type')
        string = kwargs.get('string')
        ciphered = XOR.cipher(key=self.keys[type0], string=string)
        encoded = base64.b64encode(ciphered.encode()).decode() #we need a string, not bytes tbh
        return encoded
    
    def decode0(self, **kwargs):
        type0 = kwargs.get('type')
        string = kwargs.get('string')
        ciphered = base64.b64decode(string)
        decoded = XOR.cipher(key=self.keys[type0], string=ciphered.decode())
        return decoded
