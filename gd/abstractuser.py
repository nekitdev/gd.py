from .typing import (
    AbstractUser, Comment, Iterable, Level, Optional,
    List, Union, User
)

from .abstractentity import AbstractEntity

from .utils.enums import CommentStrategy, LevelLeaderboardStrategy
from .utils.filters import Filters
from .utils.search_utils import get as _get
from .utils.text_tools import make_repr


class AbstractUser(AbstractEntity):
    """Class that represents an Abstract Geometry Dash User.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __repr__(self) -> str:
        info = {
            'name': repr(self.name),
            'id': self.id,
            'account_id': self.account_id
        }
        return make_repr(self, info)

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """:class:`str`: String representing name of the user."""
        return self.options.get('name', '')

    @property
    def account_id(self) -> int:
        """:class:`int`: Account ID of the user."""
        return self.options.get('account_id', 0)

    @property
    def _dict_for_parse(self) -> dict:
        return {
            k: getattr(self, k) for k in ('name', 'id', 'account_id')
        }

    def is_registered(self) -> bool:
        """:class:`bool`: Indicates whether user is registered or not."""
        return self.id > 0 and self.account_id > 0

    def as_user(self) -> AbstractUser:
        """Returns :class:`.AbstractUser` object.

        This is used mainly in subclasses.

        Returns
        -------
        :class:`.AbstractUser`
            Abstract User from given object.
        """
        return self.client.make_user(self)

    async def to_user(self) -> User:
        """|coro|

        Convert ``self`` to :class:`.User` object.

        Returns
        -------
        :class:`.User`
            A user object corresponding to the abstract one.
        """
        return await self.client.get_user(self.account_id)

    async def update(self) -> None:
        """|coro|

        Update ``self``.
        """
        new = await self.client.fetch_user(self.account_id)
        self.options = new.options

    async def send(self, subject: str, body: str) -> None:
        """|coro|

        Send the message to ``self``. Requires logged client.

        Parameters
        ----------
        subject: :class:`str`
            The subject of the message.

        body: :class:`str`
            The body of the message.

        from_client: :class:`.Client`
            A logged in client to send a message from. If ``None``,
            defaults to a client attached to this user.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a message.
        """
        await self.client.send_message(self, subject, body)

    async def block(self) -> None:
        """|coro|

        Block a user. Requires logged in client.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to block a user.
        """
        await self.client.block(self)

    async def unblock(self) -> None:
        """|coro|

        Unblock a user. Requires logged in client.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to unblock a user.
        """
        await self.client.unblock(self)

    async def unfriend(self) -> None:
        """|coro|

        Try to unfriend a user. Requires logged in client.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to unfriend a user.
        """
        await self.client.unfriend(self)

    async def send_friend_request(self, message: Optional[str] = None) -> None:
        """|coro|

        Send a friend request to a user.

        .. note::

            This function does not raise any error if request was already sent.

        Parameters
        ----------
        message: :class:`str`
            A message to attach to a request.

        Raises
        ------
        :exc:`.MissingAccess`
            Failed to send a friend request to user.
        """
        await self.client.send_friend_request(self, message)

    async def get_levels_on_page(self, page: int = 0, *, raise_errors: bool = True) -> List[Level]:
        """|coro|

        Fetches user's levels on a given page.

        This function is equivalent to calling:

        .. code-block:: python3

            await self.client.search_levels_on_page(
                page=page, filters=gd.Filters.setup_by_user(),
                user=self, raise_errors=raise_errors
            )
            # 'self' is an AbstractUser instance here.

        Parameters
        ----------
        page: :class:`int`
            Page to look for levels at.

        raise_errors: :class:`bool`
            Whether to raise errors if nothing was found or fetching failed.

        Returns
        -------
        List[:class:`.Level`]
            All levels found. Can be an empty list.
        """
        filters = Filters.setup_by_user()
        return await self.client.search_levels_on_page(
            page=page, filters=filters, user=self, raise_errors=raise_errors)

    async def get_levels(self, pages: Iterable[int] = range(10)) -> List[Level]:
        """|coro|

        Gets levels on specified pages.

        This is equivalent to calling:

        .. code-block:: python3

            return await self.client.search_levels(
                pages=pages, filters=gd.Filters.setup_by_user(), user=self
            )
            # where 'self' is an AbstractUser instance.

        Parameters
        ----------
        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        Returns
        -------
        List[:class:`.Level`]
            List of levels found. Can be an empty list.
        """
        filters = Filters.setup_by_user()
        return await self.client.search_levels(pages=pages, filters=filters, user=self)

    async def get_page_comments(self, page: int = 0) -> List[Comment]:
        """|coro|

        Gets user's profile comments on a specific page.

        This is equivalent to:

        .. code-block:: python3

            await self.retrieve_page_comments('profile', page)
        """
        return await self.retrieve_page_comments('profile', page)

    async def get_page_comment_history(
        self, strategy: Union[int, str, CommentStrategy] = 0, page: int = 0
    ) -> List[Comment]:
        """|coro|

        Retrieves user's level comments. (history)

        Equivalent to calling:

        .. code-block:: python3

            await self.retrieve_page_comments('profile', page, strategy=strategy)
        """
        return await self.retrieve_page_comments('level', page, strategy=strategy)

    async def get_comments(self, pages: Optional[Iterable[int]] = range(10)) -> List[Comment]:
        """|coro|

        Gets user's profile comments on specific pages.

        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments('profile', pages)
        """
        return await self.retrieve_comments('profile', pages)

    async def get_comment_history(
        self, strategy: Union[int, str, CommentStrategy] = 0, pages: Optional[Iterable[int]] = range(10)
    ) -> List[Comment]:
        """|coro|

        Gets user's level (history) comments on specific pages.

        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments('level', pages, strategy=strategy)
        """
        return await self.retrieve_comments('level', pages, strategy=strategy)

    async def retrieve_page_comments(
        self, type: str = 'profile', page: int = 0, *, raise_errors: bool = True,
        strategy: Union[int, str, CommentStrategy] = 0
    ) -> List[Comment]:
        """|coro|

        Utilizes getting comments. This is used in two other methods,
        :meth:`.User.get_page_comments` and :meth:`.User.get_page_comment_history`.

        Parameters
        ----------
        type: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        page: :class:`int`
            Page to look comments at.

        raise_errors: :class:`bool`
            Indicates whether :exc:`.NothingFound` should be raised.
            Should be set to false when getting several pages of comments,
            like in :meth:`.User.retrieve_comments`.

        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            A strategy to apply when searching. This is converted to :class:`.CommentStrategy`
            using :func:`.utils.value_to_enum`.

        Returns
        -------
        List[:class:`.Comment`]
            List of all comments retrieved, if comments were found.

        Raises
        ------
        :exc:`.NothingFound`
            No comments were found.
        """
        return await self.client.retrieve_page_comments(
            self, type=type, page=page, raise_errors=raise_errors, strategy=strategy)

    async def retrieve_comments(
        self, type: str = 'profile', pages: Optional[Iterable[int]] = range(10),
        strategy: Union[int, str, CommentStrategy] = 0
    ) -> List[Comment]:
        """|coro|

        Utilizes getting comments on specified pages.

        Parameters
        ----------
        type: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        strategy: Union[:class:`int`, :class:`str`, :class:`.CommentStrategy`]
            A strategy to apply when searching. This is converted to :class:`.CommentStrategy`
            using :func:`.utils.value_to_enum`.

        Returns
        -------
        List[:class:`.Comment`]
            List of comments found. Can be an empty list.
        """
        return await self.client.retrieve_comments(self, type=type, pages=pages, strategy=strategy)


class LevelRecord(AbstractUser):
    """Class that represents Geometry Dash User's Level Record.
    This class is derived from :class:`.AbstractUser`.
    """
    def __repr__(self) -> str:
        info = self.options.copy()
        info.pop('client', None)
        return make_repr(self, info)

    async def update(self) -> None:
        """|coro|

        Update ``self``.
        """
        from .level import Level  # this is a hack because *circular imports*

        records = await Level(id=self.level_id, client=self.client).get_leaderboard(self.type.value)
        record = _get(records, account_id=self.account_id)

        if record is not None:
            self.options = record.options

    @property
    def level_id(self) -> int:
        """:class:`int`: An integer representing ID of the level the record was retrieved from."""
        return self.options.get('level_id', 0)

    @property
    def percentage(self) -> int:
        """:class:`int`: Percentage of the record."""
        return self.options.get('percentage', 0)

    @property
    def coins(self) -> int:
        """:class:`int`: Amount of coins collected."""
        return self.options.get('coins', 0)

    @property
    def timestamp(self) -> str:
        """:class:`str`: Human-readable string representation of a timestamp."""
        return self.options.get('timestamp', 'unknown')

    @property
    def lb_place(self) -> int:
        """:class:`int`: User's place in leaderboard. ``0`` if not set."""
        return self.options.get('lb_place', 0)

    @property
    def type(self) -> LevelLeaderboardStrategy:
        return LevelLeaderboardStrategy.from_value(self.options.get('type', 0))
