class Rectangle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Sprite:
    def __init__(self, **options):
        self.options = options
    
    def __str__(self):
        res = f'[gd.Sprite]\n[Name:{self.name}]\n[Offset:{self.offset}]\n[Size:{self.size}]\n[Source_Size:{self.source_size}]\n[UpLeftCorner_Coord:{self.upleft_corner}]\n[Is_Rotated:{self.is_rotated()}]'
        return res
    
    def __repr__(self):
        formatted_size = 'x'.join(map(str, self.size))
        ret = f'<gd.Sprite: name={repr(self.name)}, id={self.id} size={formatted_size}, is_rotated={self.is_rotated()}>'
        return ret
        
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