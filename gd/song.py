# from .errors import error
from .abstractentity import AbstractEntity
from .utils.wrap_tools import _make_repr

class Song(AbstractEntity):
    """Class that represents Geometry Dash/Newgrounds songs."""
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
        """:class:`int`: An ID of the song."""
        return self.options.get('id')

    @property
    def name(self):
        """:class:`str`: A name of the song."""
        return self.options.get('name')

    @property
    def size(self):
        """:class:`float`: A float representing size of the song, in megabytes."""
        return self.options.get('size')

    @property
    def author(self):
        """:class:`str`: An author of the song."""
        return self.options.get('author')
    
    @property
    def link(self):
        """:class:`str` A link to the song on Newgrounds, e.g. ``.../audio/listen/id``."""
        return self.options.get('links')[0]

    @property
    def dl_link(self):
        """:class:`str`: A link to download the song, used in :meth:`.Song.download`."""
        return self.options.get('links')[1]

    def is_custom(self):
        """:class:`bool`: Indicates whether the song is custom or not."""
        return self.options.get('custom')

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
