class Sprite:
    def __init__(self, **options):
        self.options = options
    
    def __str__(self):
        res = f'[gd.Sprite]\n[Name:{self.name}]\n[Offset:({self.offset.x}, {self.offset.y})]\n[Size:({self.size.x}, {self.size.y})]\n[Source_Size:({self.source_size.x}, {self.source_size.y})]\n[Is_Rotated:{self.is_rotated()}]'
        return res

    @property
    def name(self):
        return self.options.get('name')
    @property
    def offset(self):
        return self.options.get('offset')
    @property
    def size(self):
        return self.options.get('size')
    @property
    def source_size(self):  
        return self.options.get('source_size')
    
    def is_rotated(self):
        return self.options.get('is_rotated')
    
    def duplicate(self):
        return Sprite(
            name = self.name + 'D',
            offset = self.offset,
            size = self.size,
            source_size = self.source_size,
            is_rotated = self.is_rotated()
        )