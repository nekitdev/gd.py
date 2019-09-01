from ..utils.wrap_tools import make_repr

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.width, self.height = w, h

    @property
    def size(self):
        return self.width, self.height

    def get_coords(self):
        return self.x, self.y

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
        return make_repr(self, info)

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

    def update_offset(self, x1, y1):
        x, y = self.offset
        x += x1
        y += y1
        self.options['offset'] = (x, y)

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
            is_rotated = self.is_rotated(),
            rectangle = self.get_rectangle()
        )