import logging
from io import BytesIO

from PIL import Image, ImageOps

from ..errors import FailedCaptcha
from .wrap_tools import benchmark

border = (5, 8, 16, 7)  # borders to crop
# we recieve picture 65x25 from gd server (65*25=1625 pixels to iterate through)
# and then we can cut borders, getting 44x10 image (44*10=440 pixels to iterate through)
# so, amount of iterations is 3.693(18) times lower.

log = logging.getLogger(__name__)

class Captcha:
    @classmethod
    @benchmark
    def solve(cls, buffer, should_log: bool = False):
        """Solves GD Captcha from given buffer/bytes.

        Method: get_image -> crop -> walk through pixels
        -> mark bright pixels -> predict digits from existing setup
        -> connect digits -> return

        This is used to make operations like changing username possible.

        Parameters
        ----------
        buffer: :class:`bytes`
            Bytes to get the Captcha image from.
            Converted to BytesIO to make initialization of image
            a little bit faster.

        should_log: :class:`bool`
            Indicates if message about solved Captcha should be logged.

        Returns
        -------
        :class:`int`
            Code that is shown in Captcha.
        """
        # get image from BytesIO, then crop the borders
        img = ImageOps.crop(Image.open(BytesIO(buffer)), border)
        pixels = img.load()  # load as pixel map
        predict = cls.walk_through(pixels, img.size)
        code = cls.connect_result(predict)
        if should_log:
            log.debug("Solved a Captcha. The code was %s.", code)
        return code

    @classmethod
    def walk_through(cls, pixel_map, size):
        """The main body of Captcha solving.

        Walks through pixels, finds bright ones, stores them,
        tries to predict each digit.

        Parameters
        ----------
        pixel_map: :class:`PIL.PixelAccess`
            A map of pixels to walk through.

        size: Tuple[int, int]
            A tuple representing width and height of the image.

        Returns
        -------
        :class:`list`
            A list, containing five digits to solve the Captcha.
        """
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
                    predicted = cls.predict_digit(lst[g])
                    final_res.append(predicted)
                    g += 1
            else:
                s = lst[g]
                if len(s) < 2:
                    s.append(temp)
        return final_res

    @classmethod
    def predict_digit(cls, res):
        cases = cls.init_numbers()
        try:
            return cases.index(res)
        except ValueError:
            raise FailedCaptcha(f'Unknown result for digit was recieved: {res}.')

    @classmethod
    def init_numbers(cls):
        """Get bright pixel index setups for number predicting."""
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

    @classmethod
    def connect_result(cls, res):
        return int(str().join(map(str, res)))