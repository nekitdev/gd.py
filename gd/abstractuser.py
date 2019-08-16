import asyncio
import itertools

from typing import Sequence, Union

from .abstractentity import AbstractEntity
from .session import _session
from .utils.wrap_tools import make_repr, check

class AbstractUser(AbstractEntity):
    """Class that represents an Abstract Geometry Dash User.
    This class is derived from :class:`.AbstractEntity`.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self.options = options
    
    def __repr__(self):
        info = {
            'name': repr(self.name),
            'id': self.id,
            'account_id': self.account_id
        }
        return make_repr(self, info)
        
    @property
    def name(self):
        """:class:`str`: String representing name of the user."""
        return self.options.get('name')
    
    @property
    def account_id(self):
        """:class:`int`: Account ID of the user."""
        return self.options.get('account_id')

    @property
    def _dict_for_parse(self):
        return {
            k: getattr(self, k) for k in ('name', 'id', 'account_id')
        }

    async def to_user(self):
        """|coro|

        Convert ``self`` to :class:`.User` object.

        Returns
        -------
        :class:`.User`
            A user object corresponding to the abstract one.
        """
        return await _session.get_user(self.account_id, client=self._client)

    async def send(self, subject: str, body: str, *, from_client=None):
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
        client = from_client if from_client is not None else self._client
        check.is_logged_obj(client, 'send')
        await _session.send_message(target=self, subject=subject, body=body, client=client)

    async def get_page_comments(self, page: int = 0):
        """|coro|

        Gets user's profile comments on a specific page.

        This is equivalent to:

        .. code-block:: python3

            await self.retrieve_page_comments('profile', page)
        """
        return await self.retrieve_page_comments('profile', page)

    async def get_page_comment_history(self, page: int = 0):
        """|coro|

        Gets user's level (history) comments on a specific page.

        This is equivalent to:

        .. code-block:: python3

            await self.retrieve_page_comments('level', page)
        """
        return await self.retrieve_page_comments('level', page)

    async def get_comments(
        self, pages: Sequence[int] = [],
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 5.0
    ):
        """|coro|

        Gets user's profile comments on specific pages.

        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments(
                'profile', pages, sort_by_page=sort_by_page, timeout=timeout
            )
        """
        return await self.retrieve_comments(
            'profile', pages, sort_by_page=sort_by_page, timeout=timeout
        )

    async def get_comment_history(
        self, pages: Sequence[int] = [],
        *, sort_by_page: bool = True,
        timeout: Union[int, float] = 5.0
    ):
        """|coro|

        Gets user's level (history) comments on specific pages.
        
        This is equivalent to the following:

        .. code-block:: python3

            await self.retrieve_comments(
                'level', pages, sort_by_page=sort_by_page, timeout=timeout
            )
        """
        return await self.retrieve_comments(
            'level', pages, sort_by_page=sort_by_page, timeout=timeout
        )

    async def retrieve_page_comments(
        self, typeof: str = 'profile', page: int = 0, *, raise_errors: bool = True
    ):
        """|coro|

        Utilizes getting comments. This is used in two other methods,
        :meth:`.User.get_page_comments` and :meth:`.User.get_page_comment_history`.

        Parameters
        ----------
        typeof: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        page: :class:`int`
            Page to look comments at.

        raise_errors: :class:`bool`
            Indicates whether :exc:`.NothingFound` should be raised.
            Should be set to false when getting several pages of comments,
            like in :meth:`.User.retrieve_comments`.

        Returns
        -------
        List[:class:`.Comment`]
            List of all comments retrieved, if comments were found.

        Raises
        ------
        :exc:`.NothingFound`
            No comments were found.        
        """
        return await _session.retrieve_page_comments(
            typeof=typeof, user=self, page=page, raise_errors=raise_errors
        )

    async def retrieve_comments(
        self, typeof: str = 'profile', pages: Sequence[int] = [],
        *, sort_by_page: bool = True, timeout: Union[int, float] = 10.0
    ):
        """|coro|

        Utilizes getting comments on specified pages.

        Parameters
        ----------
        typeof: :class:`str`
            Type of comments to retrieve. Either `'profile'` or `'level'`.
            Defaults to `'profile'`.

        pages: Sequence[:class:`int`]
            Pages to look at, represented as a finite sequence, so iterations can be performed.

        sort_by_page: :class:`bool`
            Indicates whether returned comments should be sorted by page.

        timeout: Union[:class:`int`, :class:`float`]
            Timeout to stop requesting after it occurs.
            Used to prevent insanely long responses.

        Returns
        -------
        List[:class:`.Comment`]
            List of comments found. Can be an empty list.
        """
        return await _session.retrieve_comments(
            typeof=typeof, user=self, pages=pages, sort_by_page=sort_by_page, timeout=timeout
        )
