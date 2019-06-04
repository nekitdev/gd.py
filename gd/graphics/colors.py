from ..utils.converter import Converter
from PIL import Image

class Color:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b

	def __str__(self):
		res = f'[gd.Color]\n[Index:{Converter.to_ordinal(self.index)}]\n[RGB:{self.to_rgb()}]\n[HEX:{self.to_hex()}]'
		return res

	@property
	def index(self):
		return list(colors.values()).index(self)

	def to_hex(self):
		res = '#'; mapped = list(map(hex, self.to_rgb()))
		for hex_elem in mapped:
			temp = hex_elem[2:]
			res += temp if len(temp) is 2 else '0' + temp
		return res
	
	def show(self): #don't put this in for loops... please?
		img = Image.new("RGB", (16, 16), self.to_rgb())
		img.show()
	
	def to_rgb(self):
		res = (self.r, self.g, self.b)
		return res

colors = { # I know it can be a list
    0: Color(125, 255, 0),
	1: Color(0, 255, 0),
	2: Color(0, 255, 125),
	3: Color(0, 255, 255),
	4: Color(0, 125, 255),
	5: Color(0, 0, 255),
	6: Color(125, 0, 255),
	7: Color(255, 0, 255),
	8: Color(255, 0, 125),
	9: Color(255, 0, 0),
	10: Color(255, 125, 0),
	11: Color(255, 255, 0),
	12: Color(255, 255, 255),
	13: Color(185, 0, 255),
	14: Color(255, 185, 0),
	15: Color(0, 0, 0),
	16: Color(0, 200, 255),
	17: Color(175, 175, 175),
	18: Color(90, 90, 90),
	19: Color(255, 125, 125),
	20: Color(0, 175, 75),
	21: Color(0, 125, 125),
	22: Color(0, 75, 175),
	23: Color(75, 0, 175),
	24: Color(125, 0, 125),
	25: Color(175, 0, 75),
	26: Color(175, 75, 0),
	27: Color(125, 125, 0),
	28: Color(75, 175, 0),
	29: Color(255, 75, 0),
	30: Color(150, 50, 0),
	31: Color(150, 100, 0),
	32: Color(100, 150, 0),
	33: Color(0, 150, 100),
	34: Color(0, 100, 150),
	35: Color(100, 0, 150),
	36: Color(150, 0, 100),
	37: Color(150, 0, 0),
	38: Color(0, 150, 0),
	39: Color(0, 0, 150),
	40: Color(125, 255, 175),
	41: Color(125, 125, 255),
}