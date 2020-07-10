from gd.abstractentity import AbstractEntity
from gd.abstractuser import AbstractUser

from gd.colors import Color

from gd.typing import Client, Comment, Union

from gd.utils.enums import CommentType
from gd.utils.indexer import Index
from gd.utils.parser import ExtDict
from gd.utils.text_tools import make_repr
from gd.utils.crypto.coders import Coder


class Comment(AbstractEntity):
    """Class that represents a Profile/Level comment in Geometry Dash.
    This class is derived from :class:`.AbstractEntity`.
    """

    def __repr__(self) -> str:
        info = {"author": self.author, "id": self.id, "rating": self.rating}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.body)

    @classmethod
    def from_data(
        cls, data: ExtDict, author: Union[ExtDict, AbstractUser], client: Client
    ) -> Comment:
        if isinstance(author, ExtDict):
            if any(key.isdigit() for key in author.keys()):
                author = AbstractUser.from_data(author, client=client)
            else:
                author = AbstractUser(**author, client=client)

        color_string = data.get(Index.COMMENT_COLOR, "255,255,255")
        color = Color.from_rgb(*map(int, color_string.split(",")))

        return cls(
            body=Coder.do_base64(data.get(Index.COMMENT_BODY, ""), encode=False, errors="replace"),
            rating=data.getcast(Index.COMMENT_RATING, 0, int),
            timestamp=data.get(Index.COMMENT_TIMESTAMP, "unknown"),
            id=data.getcast(Index.COMMENT_ID, 0, int),
            is_spam=bool(data.getcast(Index.COMMENT_IS_SPAM, 0, int)),
            type=CommentType.from_value(data.getcast(Index.COMMENT_TYPE, 0, int), 0),
            color=color,
            level_id=data.getcast(Index.COMMENT_LEVEL_ID, 0, int),
            level_percentage=data.getcast(Index.COMMENT_LEVEL_PERCENTAGE, -1, int),
            author=author,
            client=client,
        )

    @property
    def body(self) -> str:
        """:class:`str`: Returns body of the comment."""
        return self.options.get("body", "")

    @property
    def rating(self) -> int:
        """:class:`int`: Rating of the comment."""
        return self.options.get("rating", 0)

    @property
    def timestamp(self) -> str:
        """:class:`str`: A human-readable timestamp representing how long ago the comment was created."""
        return self.options.get("timestamp", "unknown")

    @property
    def author(self) -> AbstractUser:
        """:class:`.AbstractUser`: An author of the comment."""
        return self.options.get("author", AbstractUser(client=self.client))

    @property
    def type(self) -> CommentType:
        """:class:`.CommentType`: Whether comment is on profile or on a level."""
        return CommentType.from_value(self.options.get("type", 0))

    @property
    def level_id(self) -> int:
        """:class:`int`: Level ID of a level the comment is on, if present. ``0`` if profile comment."""
        return self.options.get("level_id", 0)

    @property
    def level_percentage(self) -> int:
        """:class:`int`: Level highscore linked to a comment, if present. ``-1`` if profile comment."""
        return self.options.get("level_percentage", -1)

    @property
    def color(self) -> Color:
        """:class:`.Color`: Color of the comment. Oftenly equals ``gd.Color(0xffffff)``."""
        return self.options.get("color", Color(0xFFFFFF))

    def is_spam(self) -> bool:
        """:class:`bool`: Indicates whether a comment is marked as spam. ``False`` if profile comment."""
        return self.options.get("is_spam", False)

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
