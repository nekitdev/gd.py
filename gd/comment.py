from .abstractentity import AbstractEntity
from .session import GDSession

from .utils.context import ctx
from .utils.wrap_tools import _make_repr, check

_session = GDSession()

class Comment(AbstractEntity):
    """Class that represents a Profile/Level comment in Geometry Dash."""
    def __init__(self, **options):
        super().__init__(**options)
        # self._client = client
        self.options = options
    
    def __repr__(self):
        info = {
            'author': self.author,
            'body': repr(self.body),
            'id': self.id,
            'rating': self.rating
        }
        return _make_repr(self, info)

    @property
    def body(self):
        return self.options.get('body')

    @property
    def rating(self):
        return self.options.get('rating')

    @property
    def timestamp(self):
        return self.options.get('timestamp')

    @property
    def author(self):
        return self.options.get('author')

    @property
    def typeof(self):
        return self.options.get('type')

    @property
    def level_id(self):
        return self.options.get('level_id')

    @property
    def level_percentage(self):
        return self.options.get('level_percentage')

    @property
    def page(self):
        return self.options.get('page')

    def is_disliked(self):
        return abs(self.rating) != self.rating

    @check.is_logged(ctx)
    async def delete(self):
        """|coro|

        Deletes a comment from Geometry Dash servers.

        Obviously, only comments of client logged in using :meth:`.Client.login` can be deleted.

        The normal behaviour of the server is returning 1 if comment was deleted,
        so the error is raised on response != 1.

        Raises
        ------
        :exc:`.MissingAccess`
            Server did not return 1, which means comment was not deleted.
        """
        await _session.delete_comment(self)

# TO_DO: add docs here if needed
