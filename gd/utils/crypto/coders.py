from .xor_cipher import XORCipher as XOR
import base64
import hashlib

class Coder:

    def __init__(self):
        self.keys = {
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
        self.salts = {
            'level': 'xI25fpAapCQg',
            'comment': 'xPT6iUrtws0J',
            'challenges': '',
            'rewards': '',
            'like_rate': 'ysg6pUrtjn0J',
            'userscore': 'xI35fsAapCRg',
            'levelscore': 'yPg6pUrtWn0J'
        }

    def encode0(self, **kwargs):
        type0 = kwargs.get('type')
        string = kwargs.get('string')
        ciphered = XOR.cipher(key=self.keys[type0], string=string)
        encoded = base64.b64encode(ciphered.encode()).decode()  # we need a string, not bytes tbh
        return encoded
    
    def decode0(self, **kwargs):
        type0 = kwargs.get('type')
        string = kwargs.get('string')
        ciphered = base64.b64decode(string)
        decoded = XOR.cipher(key=self.keys[type0], string=ciphered.decode())
        return decoded

    def gen_chk(self, **kwargs):
        type0 = kwargs.get('type')
        values = list(map(str, kwargs.get('values')))
        salt = self.salts[type0]
        string = ''
        if (self.keys[type0] == self.keys['levelscore']):
            i = 0
            while (i < len(values)-1):
                string += values[i]
                if (i == 7):
                    string += '1'
                i += 1
            string += salt + values[len(values)-1]
        else:
            for value in values:
                string += value
            string += salt
        hashed = hashlib.sha1(string.encode()).hexdigest()
        xored = XOR.cipher(key=self.keys[type0], string=hashed)
        encoded = base64.b64encode(xored.encode()).decode()  # again, we're sending a string, not bytes
        return encoded
    
    def gen_level_lb_seed(self, jumps: int, percentage: int, seconds: int):
        res = 1482 + (jumps + 3991) * (percentage + 8354) + pow(seconds + 4085, 2) - 50028039
        return res