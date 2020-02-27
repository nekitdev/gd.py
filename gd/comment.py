from .abstractentity import AbstractEntity
from .abstractuser import AbstractUser

from .colors import Color

from .utils.enums import CommentType
from .utils.text_tools import make_repr


class Comment(AbstractEntity):
    """Class that represents a Profile/Level comment in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __repr__(self) -> str:
        info = {
            'author': self.author,
            'id': self.id,
            'rating': self.rating
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.body)

    @property
    def body(self) -> str:
        """:class:`str`: Returns body of the comment."""
        return self.options.get('body', '')

    @property
    def rating(self) -> int:
        """:class:`int`: Rating of the comment."""
        return self.options.get('rating', 0)

    @property
    def timestamp(self) -> str:
        """:class:`str`: A human-readable timestamp representing how long ago the comment was created."""
        return self.options.get('timestamp', 'unknown')

    @property
    def author(self) -> AbstractUser:
        """:class:`.AbstractUser`: An author of the comment."""
        return self.options.get('author', AbstractUser())

    @property
    def type(self) -> CommentType:
        """:class:`.CommentType`: Whether comment is on profile or on a level."""
        return CommentType.from_value(self.options.get('type', 0))

    @property
    def level_id(self) -> int:
        """:class:`int`: Level ID of a level the comment is on, if present. ``0`` if profile comment."""
        return self.options.get('level_id', 0)

    @property
    def level_percentage(self) -> int:
        """:class:`int`: Level highscore linked to a comment, if present. ``-1`` if profile comment."""
        return self.options.get('level_percentage', -1)

    @property
    def color(self) -> Color:
        """:class:`.Color`: Color of the comment. Oftenly equals ``gd.Color(0xffffff)``."""
        return self.options.get('color', Color(0xffffff))

    def is_spam(self) -> bool:
        """:class:`bool`: Indicates whether a comment is marked as spam. ``False`` if profile comment."""
        return self.options.get('is_spam', False)

    def is_disliked(self) -> bool:
        """:class:`bool`: Indicates whether a comment is disliked or not."""
        return self.rating < 0

    async def like(self) -> None:
        """|coro|

        Likes a comment.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to like a comment.
        """
        await self.client.like(self)

    async def dislike(self) -> None:
        """|coro|

        Dislikes a comment.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to dislike a comment.
        """
        await self.client.dislike(self)

    async def delete(self) -> None:
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
        await self.client.delete_comment(self)
