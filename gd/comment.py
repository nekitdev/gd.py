from gd.abstract_entity import AbstractEntity
from gd.color import Color
from gd.datetime import datetime
from gd.enums import CommentType
from gd.model import CommentModel  # type: ignore
from gd.text_utils import make_repr
from gd.typing import Optional, TYPE_CHECKING
from gd.user import User

__all__ = ("Comment",)

if TYPE_CHECKING:
    from gd.client import Client  # noqa
    from gd.level import Level  # noqa


class Comment(AbstractEntity):
    """Class that represents a Profile/Level comment in Geometry Dash.
    This class is derived from :class:`~gd.AbstractEntity`.

    .. container:: operations

        .. describe:: x == y

            Check if two objects are equal. Compared by hash and type.

        .. describe:: x != y

            Check if two objects are not equal.

        .. describe:: str(x)
            Return content of the comment.

        .. describe:: repr(x)
            Return representation of the comment, useful for debugging.

        .. describe:: hash(x)

            Returns ``hash(self.hash_str)``.
    """

    def __repr__(self) -> str:
        info = {"id": self.id, "author": self.author, "rating": self.rating}
        return make_repr(self, info)

    def __str__(self) -> str:
        return str(self.content)

    @classmethod
    def from_model(
        cls, model: CommentModel, *, client: Optional["Client"] = None, user: Optional[User] = None
    ) -> "Comment":
        """Initialize :class:`~gd.Comment` from :class:`~gd.model.CommentModel`.

        Parameters
        ----------

        model: :class:`~gd.model.CommentModel`
            Comment model to use.

        client: :class:`~typing.Optional`[:class:`~gd.Client`]
            Client to attach.

        user: :class:`~typing.Optional`[:class:`~gd.User`]
            Author of the comment to use, if not in model.

        Returns
        -------

        :class:`~gd.Comment`
            New comment instance.
        """
        if user is None:
            model_user = model.user

            if model_user is None:
                user = User()

            else:
                user = User.from_model(model_user)

        comment_model = model.inner

        return cls(
            id=comment_model.id,
            level_id=comment_model.level_id,
            content=comment_model.content,
            rating=comment_model.rating,
            is_spam=comment_model.is_spam,
            created_at=comment_model.created_at,
            level_percent=comment_model.level_percent,
            color=comment_model.color,
            author=user.attach_client(client),
            client=client,
        )

    @property
    def content(self) -> str:
        """:class:`str`: Content of the comment."""
        return self.options.get("content", "")

    body = content

    @property
    def rating(self) -> int:
        """:class:`int`: Rating of the comment."""
        return self.options.get("rating", 0)

    @property
    def created_at(self) -> Optional[datetime]:
        """Optional[:class:`~py:datetime.datetime`]:
        Timestamp representing when the comment was created.
        """
        return self.options.get("created_at")

    @property
    def author(self) -> User:
        """:class:`~gd.User`: An author of the comment."""
        return self.options.get("author", User(client=self.client_unchecked))

    @property
    def type(self) -> CommentType:
        """:class:`~gd.CommentType`: Whether comment is on profile or on a level."""
        return CommentType.from_value(self.options.get("type", 0))

    @property
    def level_id(self) -> int:
        """:class:`int`: Level ID of a level the comment is on. ``0`` if profile comment."""
        return self.options.get("level_id", 0)

    @property
    def level_percent(self) -> int:
        """:class:`int`: Level highscore linked to a comment. ``-1`` if profile comment."""
        return self.options.get("level_percent", -1)

    @property
    def color(self) -> Color:
        """:class:`~gd.Color`: Color of the comment. Often equals ``gd.Color(0xffffff)``."""
        return self.options.get("color", Color(0xFFFFFF))

    def is_spam(self) -> bool:
        """:class:`bool`: Indicates whether a comment is marked as spam.
        ``False`` if profile comment.
        """
        return self.options.get("is_spam", False)

    def is_disliked(self) -> bool:
        """:class:`bool`: Indicates whether a comment is disliked or not."""
        return self.rating < 0

    async def get_level(self, get_data: bool = True) -> "Level":
        return await self.client.get_level(self.level_id, get_data=get_data)

    async def like(self) -> None:
        """Likes a comment.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to like a comment.

        :exc:`~gd.HTTPStatusError`
            Server returned error status codes. (``4XX`` or ``5XX`` and above).

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.like(self)

    async def dislike(self) -> None:
        """Dislikes a comment.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Failed to dislike a comment.

        :exc:`~gd.HTTPStatusError`
            Server returned error status codes. (``4XX`` or ``5XX`` and above).

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.dislike(self)

    async def delete(self) -> None:
        """Deletes a comment from Geometry Dash servers.

        Raises
        ------
        :exc:`~gd.MissingAccess`
            Comment was not deleted.

        :exc:`~gd.HTTPStatusError`
            Server returned error status codes. (``4XX`` or ``5XX`` and above).

        :exc:`~gd.HTTPError`
            Failed to process the request.
        """
        await self.client.delete_comment(self)
