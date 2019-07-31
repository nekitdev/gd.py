from ..utils.wrap_tools import _make_repr
from ..utils.converter import Converter

class Color:
	def __init__(self, r, g, b):
		self.r = r
		self.g = g
		self.b = b
		self.a = 255
	
	def __repr__(self):
		info = {
		    'index': Converter.to_ordinal(self.index),
		    'hex': self.to_hex()
		}
		return _make_repr(self, info)
		
	@property
	def index(self):
		return colors.index(self)
	
	def to_rgb(self):
		return (self.r, self.g, self.b)
		
	def to_rgba(self):
		return self.to_rgb() + (self.a,)
		
	def to_hex(self):
		res = '#'
		for c in self.to_rgb():
			res += '{:02x}'.format(c)
		return res

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