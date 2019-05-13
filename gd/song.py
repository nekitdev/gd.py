from .utils.errors import error

class Song:
    def __init__(self, **options):
        self._name = options.get('name')
        self._author = options.get('author')
        self._id = options.get('_id')
        self._size = options.get('size')
        self._size_mb = options.get('size_mb')
        self._links = options.get('links')
    
    def __str__(self):
        return self.get_all_info()

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def size(self):
        return self._size

    @property
    def size_mb(self):
        return self._size_mb

    @property
    def author(self):
        return self._author
    
    @property
    def link(self):
        return self._links[0]

    @property
    def dl_link(self):
        return self._links[1]
    
    def get_all_info(self):
        return f"[gd.Song]\n[ID][{self.id}]\n[Name][{self.name}]\n[Author][{self.author}]\n[Links]\n[Basic][{self.link}]\n[Download][{self.dl_link}]"

    def download(self, **kwargs):
        link = self._links[1]
        path = kwargs.get('path')
        if len(kwargs) > 1:
            raise error.TooManyArguments()
        if path is None:
            pass
        else:
            pass
