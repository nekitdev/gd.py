from PIL import Image, ImageOps
from io import BytesIO
from .decorators import benchmark

border = (5, 8, 16, 7) #borders to crop
#why borders? well, let's do some quick math:
#we recieve picture 65x25 from gd server (65*25=1625 pixels to iterate through)
#and then we cut borders, getting 44x10 image (44*10=440 pixels to iterate through)
#so, amount of iterations is 3.693(18) times lower ;)

class Captcha:
    def __init__(self):
        self.status = 'empty'
    
    def __str__(self):
        res = f'[gd.Captcha]\n[Status:{self.status}]'
        return res
        
    def __repr__(self):
        res = f'<gd.Captcha: status={repr(self.status)}>'
        return res

    def solve(self, buffer, with_image=False): #if with_image is True, image of the captcha will be shown
        io_stuff = BytesIO(buffer)
        image = Image.open(io_stuff); img = ImageOps.crop(image, border) #get image from BytesIO, then crop the borders
        pixels = img.load() #size: (44, 10)
        predict = self.walk_through(pixels, img.size)
        connected = self.connect_result(predict)
        self.status = 'solved'
        if with_image: image.show()
        return connected
    
    def walk_through(self, pixel_map, size):
        a, b, c, d, e = [[] for _ in range(5)] #five empty lists (I don't like to work with five lists in one)
        g = 1 #digit index checker
        final_res = [] #we append here our predicted digits
        for i in range(size[0]): #for every column
            temp = []
            for j in range(size[1]): #for every row
                rgb = pixel_map[i, j]
                if all(rgb[i] > 200 for i in range(3)): #if pixel is white
                    temp.append(j) #append 'index' in column of pixel
            cases = {g==1:a, g==2:b, g==3:c, g==4:d, g==5:e}
            if not temp or (i+1 is size[0]):
                if cases.get(True): #if we actually have something to predict
                    predicted = self.predict_digit(cases.get(True))
                    final_res.append(predicted)
                    g += 1
            else:
                s = cases.get(True)
                if len(s) < 2: s.append(temp)
        return final_res
    
    def predict_digit(self, res):
        cases = self.init_numbers()
        return cases.index(res)
    
    def init_numbers(self):
        setup = [
            [[3,4,5,6],[2,3,4,5,6,7]],
            [[2,9],[1,2,9]],
            [[2,9],[1,2,8,9]],
            [[1,8],[0,1,8,9]],
            [[5,6],[4,5,6]],
            [[0,1,2,3,4,7],[0,1,2,3,4,7,8]],
            [[2,3,4,5,6,7],[1,2,3,4,5,6,7,8]],
            [[0,8,9],[0,7,8,9]],
            [[2,6,7],[1,2,3,5,6,7,8]],
            [[2,3],[1,2,3,4,7,8]]
        ]
        return setup

    def connect_result(self, res):
        return int(str().join(map(str, res)))