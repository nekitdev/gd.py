# from .errors import error
from .abstractentity import AbstractEntity

class Song(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
    
    def __str__(self):
        res = f"[gd.Song]\n[ID:{self.id}]\n[Name:{self.name}]\n[Author:{self.author}]\n[Links]\n[Basic:{self.link}]\n[Download:{self.dl_link}]"
        return res
    
    def __repr__(self):
        ret = f'<gd.Song: id={self.id}, name={repr(self.name)}, author={repr(self.author)}>'
        return ret

    @property
    def name(self):
        return self.options.get('name')

    @property
    def size(self):
        return self.options.get('size')

    @property
    def size_mb(self):
        return self.options.get('size_mb')

    @property
    def author(self):
        return self.options.get('author')
    
    @property
    def link(self):
        return self.options.get('links')[0]

    @property
    def dl_link(self):
        return self.options.get('links')[1]

    def download(self, path=None):
        link = self.dl_link
        if path is None:
            pass
        else:
            pass
