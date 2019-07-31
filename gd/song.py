# from .errors import error
from .abstractentity import AbstractEntity
from .utils.wrap_tools import _make_repr

class Song(AbstractEntity):
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
    
    def __repr__(self):
        info = {
            'id': self.id,
            'name': repr(self.name),
            'author': self.author
        }
        return _make_repr(self, info)

    @property
    def id(self):
        return self.options.get('id')

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

    async def download(self, path=None):
        """|coro|

        Download a song from Newgrounds.

        Parameters
        ----------
        path: Any
            A path to save a song to. Defaults to ``None``.
        
        Returns
        -------
        :class:`bytes`
            A song as bytes. Returned if path is ``None``.
        """
        link = self.dl_link
        pass  # TO_DO: Finish
