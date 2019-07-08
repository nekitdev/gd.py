from ..utils.converter import Converter
from PIL import Image

class Color:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b
		self.a = 255

	def __str__(self):
		res = f'[gd.Color]\n[Index:{Converter.to_ordinal(self.index)}]\n[RGB:{self.to_rgb()}]\n[HEX:{self.to_hex()}]'
		return res
	
	def __repr__(self):
		ret = f'<gd.Color: index={Converter.to_ordinal(self.index)}, hex={self.to_hex()}>'
		return ret
		
	@property
	def index(self):
		return colors.index(self)
	
	def to_rgb(self):
		return self.r, self.g, self.b
		
	def to_rgba(self):
		return self.r, self.g, self.b, self.a
		
	def to_hex(self):
		res = '#'; mapped = list(map(hex, self.to_rgb()))
		for hex_elem in mapped:
			temp = hex_elem[2:]
			res += temp if len(temp) is 2 else '0' + temp
		return res
	
	def show(self): #don't put this in for loops... please?
		img = Image.new("RGB", (16, 16), self.to_rgb())
		img.show()

def show_all(): #some random stuff
	total = len(colors)
	plate = Image.new("RGB", (16*total, 16), "black")
	for i in range(total):
		to_paste = Image.new("RGB", (16, 16), colors[i].to_rgb())
		corner = (16*i, 0)
		plate.paste(to_paste, corner)
	plate.show()

colors = (
	Color(125, 255, 0),
	Color(0, 255, 0),
	Color(0, 255, 125),
	Color(0, 255, 255),
	Color(0, 125, 255),
	Color(0, 0, 255),
	Color(125, 0, 255),
	Color(255, 0, 255),
	Color(255, 0, 125),
	Color(255, 0, 0),
	Color(255, 125, 0),
	Color(255, 255, 0),
	Color(255, 255, 255),
	Color(185, 0, 255),
	Color(255, 185, 0),
	Color(0, 0, 0),
	Color(0, 200, 255),
	Color(175, 175, 175),
	Color(90, 90, 90),
	Color(255, 125, 125),
	Color(0, 175, 75),
	Color(0, 125, 125),
	Color(0, 75, 175),
	Color(75, 0, 175),
	Color(125, 0, 125),
	Color(175, 0, 75),
	Color(175, 75, 0),
	Color(125, 125, 0),
	Color(75, 175, 0),
	Color(255, 75, 0),
	Color(150, 50, 0),
	Color(150, 100, 0),
	Color(100, 150, 0),
	Color(0, 150, 100),
	Color(0, 100, 150),
	Color(100, 0, 150),
	Color(150, 0, 100),
	Color(150, 0, 0),
	Color(0, 150, 0),
	Color(0, 0, 150),
	Color(125, 255, 175),
	Color(125, 125, 255),
)