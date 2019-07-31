import logging
from io import BytesIO

from PIL import Image, ImageOps

from .wrap_tools import benchmark, _make_repr

border = (5, 8, 16, 7)  # borders to crop
# why borders? well, let's do some quick math:
# we recieve picture 65x25 from gd server (65*25=1625 pixels to iterate through)
# and then we cut borders, getting 44x10 image (44*10=440 pixels to iterate through)
# so, amount of iterations is 3.693(18) times lower.

log = logging.getLogger(__name__)

class Captcha:
    def __init__(self):
        self.status = 'empty'
        
    def __repr__(self):
        info = {
            'status': repr(self.status)
        }
        return _make_repr(self, info)

    def solve(self, buffer, should_log: bool = False):
        io_bytes = BytesIO(buffer)
        img = ImageOps.crop(Image.open(io_bytes), border)  # get image from BytesIO, then crop the borders
        pixels = img.load()
        predict = self.walk_through(pixels, img.size)
        code = self.connect_result(predict)
        self.status = 'solved'
        if should_log:
            log.debug("Solved a Captcha. The code was %s.", code)
        return code
    
    def walk_through(self, pixel_map, size):
        lst = [[] for _ in range(5)]  # store
        g = 0
        final_res = []
        x, y = size
        for i in range(x):  # for every column
            temp = []
            for j in range(y):  # for every row
                rgb = pixel_map[i, j]
                if all(rgb[i] > 200 for i in range(3)):  # if pixel is white
                    temp.append(j)  # append 'index' in column of pixel
            if not temp or (i+1 == x):
                if lst[g]:  # if we actually have something to predict
                    predicted = self.predict_digit(lst[g])
                    final_res.append(predicted)
                    g += 1
            else:
                s = lst[g]
                if len(s) < 2:
                    s.append(temp)
        return final_res
    
    def predict_digit(self, res):
        cases = self.init_numbers()
        return cases.index(res)
    
    def init_numbers(self):
        setup = [
            [[3, 4, 5, 6], [2, 3, 4, 5, 6, 7]],
            [[2, 9], [1, 2, 9]],
            [[2, 9], [1, 2, 8, 9]],
            [[1, 8], [0, 1, 8, 9]],
            [[5, 6], [4, 5, 6]],
            [[0, 1, 2, 3, 4, 7], [0, 1, 2, 3, 4, 7, 8]],
            [[2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7, 8]],
            [[0, 8, 9], [0, 7, 8, 9]],
            [[2, 6, 7], [1, 2, 3, 5, 6, 7, 8]],
            [[2, 3], [1, 2, 3, 4, 7, 8]]
        ]
        return setup

    def connect_result(self, res):
        return int(str().join(map(str, res)))