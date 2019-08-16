from .abstractentity import AbstractEntity
from .session import _session

from .utils.wrap_tools import make_repr, check

class Comment(AbstractEntity):
    """Class that represents a Profile/Level comment in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
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
        return make_repr(self, info)

    @property
    def body(self):
        """:class:`str`: Returns body of the comment."""
        return self.options.get('body')

    @property
    def rating(self):
        """:class:`int`: Rating of the comment."""
        return self.options.get('rating')

    @property
    def timestamp(self):
        """:class:`str`: A human-readable timestamp representing how long ago the comment was created."""
        return self.options.get('timestamp')

    @property
    def author(self):
        """:class:`.AbstractUser`: An author of the comment."""
        return self.options.get('author')

    @property
    def typeof(self):
        """:class:`str`: Whether comment is on profile or on a level. ('level' or 'client')"""
        return self.options.get('type')

    @property
    def level_id(self):
        """:class:`int`: Level ID of a level the comment is on, if present. ``0`` if profile comment."""
        return self.options.get('level_id')

    @property
    def level_percentage(self):
        """:class:`int`: Level highscore linked to a comment, if present. ``-1`` if profile comment."""
        return self.options.get('level_percentage')

    @property
    def page(self):
        """:class:`int`: A page the comment was retrieved from."""
        return self.options.get('page')

    @property
    def color(self):
        """:class:`.Colour`: A colour of the comment. White (``#ffffff``) by default."""
        return self.options.get('color')

    def is_spam(self):
        """:class:`bool`: Indicates whether a comment is marked as spam. ``False`` if profile comment."""
        return self.options.get('is_spam')

    def is_disliked(self):
        """:class:`bool`: Indicates whether a comment is disliked or not."""
        return abs(self.rating) != self.rating

    async def delete(self, from_client=None):
        """|coro|

        Deletes a comment from Geometry Dash servers.

        Obviously, only comments of client logged in using :meth:`.Client.login` can be deleted.

        The normal behaviour of the server is returning 1 if comment was deleted,
        so the error is raised on response != 1.

        Parameters
        ----------
        from_client: :class:`.Client`
            A logged in client to delete comments of. If ``None`` or omitted,
            defaults to the one attached to this comment.

        Raises
        ------
        :exc:`.MissingAccess`
            Server did not return 1, which means comment was not deleted.
        """
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'delete')
        await _session.delete_comment(self, client=client)

# TO_DO: add docs here if needed
