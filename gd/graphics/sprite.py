from ..utils.wrap_tools import _make_repr

class Rectangle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Sprite:
    def __init__(self, **options):
        self.options = options
    
    def __repr__(self):
        info = {
            'name': repr(self.name),
            'id': self.id,
            'size': 'x'.join(map(str, self.size)),
            'is_rotated': self.is_rotated()
        }
        return _make_repr(self, info)
        
    @property
    def name(self):
        return self.options.get('name')

    @property
    def id(self):
        return self.options.get('id')

    @property
    def offset(self):
        return self.options.get('offset')

    @property
    def size(self):
        return self.options.get('size')

    @property
    def source_size(self):  
        return self.options.get('source_size')

    @property
    def upleft_corner(self):
        return self.options.get('upleft_corner')
    
    def is_rotated(self):
        return self.options.get('is_rotated')
    
    def get_rectangle(self):
        return self.options.get('rectangle')
    
    def duplicate(self):
        return Sprite(
            name = self.name + 'D',
            id = self.id,
            offset = self.offset,
            size = self.size,
            source_size = self.source_size,
            upleft_corner = self.upleft_corner,
            is_rotated = self.is_rotated(),
            rectangle = self.get_rectangle()
        )