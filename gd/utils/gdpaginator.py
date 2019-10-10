from ..errors import PagesOutOfRange
from .wrap_tools import make_repr

def paginate(iterable, per_page: int = 10):
    """A function that paginates the given iterable.

    Simply wraps iterable in :class:`.Paginator` and returns it.

    Parameters
    ----------
    iterable: Sequence[`Any`]
        A finite sequence to paginate.

    per_page: :class:`int`
        Amount of elements in iterable to present on each page.

    Returns
    -------
    :class:`.Paginator`
        A paginator that has an ``iterable`` wrapped.
    """
    return Paginator(to_paginate=iterable, per_page=per_page)

class Paginator:
    """A class that implements a pagination system.

    Parameters
    ----------
    to_paginate: Sequence[Any]
        A sequence to paginate, such that list(to_paginate) can be performed.

    per_page: :class:`int`
        Number of elements each page can have.
    """

    def __init__(self, to_paginate, per_page: int = 10):
        self._list = list(to_paginate)
        self._per_page = per_page
        self._current_page = 0
        self.reload()

    def _configure_pages(self):
        y = self._length / self._per_page
        x = round(y)

        self._pages = x+1 if x < y else x

    def __str__(self):
        return self.current_state

    def __repr__(self):
        info = {
            'can_run': self.can_run(),
            'length': self.length,
            'per_page': self.per_page,
            'pages': self.get_pages_count(),
            'current': self.get_curr_page()
        }
        return make_repr(self, info)

    def __getitem__(self, index: int):
        return self._list[index]

    def __setitem__(self, index: int, item):
        self._list[index] = item
        self.reload()

    @property
    def length(self):
        """:class:`int`: Total amount of elements in a paginator."""
        return self._length

    @property
    def per_page(self):
        """:class:`int`: Amount of elements shown on each page."""
        return self._per_page

    @property
    def list(self):
        """List[`Any`] Paginated sequence, represented as list."""
        return self._list

    @property
    def current_state(self):
        """:class:`str`: Returns a string representation of the Paginator.

        Theoretically, this is only used when printing the Paginator's state.
        """
        p = self.get_curr_page()
        per_page = self.per_page

        _from, _to = (p*per_page, (p+1)*per_page)

        return (
            '[gd.Paginator]\n'
            '[Can_Run: {can_run}]\n'
            '[Length: {length}]\n[Pages: {pages_count}]\n'
            '[Current_State]\n[Page: {page}]\n'
            '[Showing: {_from} to {_to} of {length}]'
        ).format(
            can_run=self.can_run(), length=self.length,
            pages_count=self.get_pages_count(),
            page=self.get_curr_page(), _from=_from, _to=_to
        )

    def load_from(self, iterable):
        """A function that paginates the given iterable.

        Basically reloads already created paginator with given iterable.

        Parameters
        ----------
        iterable: Sequence[`Any`]
            A finite sequence to paginate.

        per_page: :class:`int`
            Amount of elements in iterable to present on each page.
        """
        self._list = list(iterable)
        self.reload()

    def reload(self):
        """Reconfigure length and configure pages amount."""
        self._length = len(self._list)
        self._configure_pages()

    def append(self, obj):
        """Append ``obj`` to a paginated sequence, then reload."""
        self._list.append(obj)
        self.reload()

    def pop(self, index: int = -1):
        """Pops out an element.

        Deletes element with given ``index``, and returns it.
        Reloads paginator as well.
        """
        value = self._list.pop(index)
        self.reload()
        return value

    def clear(self):
        """Clears :attr:`Paginator.list`, then reloads."""
        self._list.clear()
        self.reload()

    def get_pages_count(self):
        """:class:`int`: Get current amount of pages."""
        return self._pages

    def get_curr_page(self):
        """:class:`int`: Get a number of the current page."""
        return self._current_page

    def has_next(self):
        """:class:`bool`: Indicates whether does the next page exists."""
        return True if self.get_curr_page() < self.get_pages_count() else False

    def has_prev(self):
        """:class:`bool`: Indicates if previous page is existing."""
        return True if self.get_curr_page() > 0 else False

    def can_run(self):
        """:class:`bool`: Indicates whether paginator is empty."""
        return self.length > 0

    def move_to_next(self):
        """Tries to go to the next page.

        Raises
        ------
        :exc:`.PagesOutOfRange`
            The next page does not exist.
        """
        if not self.has_next():
            raise PagesOutOfRange(
                page = self.get_curr_page() + 1,
                info = self.get_pages_count()
            )
        self._current_page += 1

    def move_to_prev(self):
        """Attempts to go to the previous page.

        Raises
        ------
        :exc:`.PagesOutOfRange`
            The previous page does not exist.
        """
        if not self.has_prev():
            raise PagesOutOfRange(
                page = self.get_curr_page() - 1,
                info = 'Page does not support negative integers.'
            )
        self._current_page -= 1

    def move_to(self, page: int):
        """Moves to the ``page`` given.

        Parameters
        ----------
        page: :class:`int`
            A page to move to.

        Raises
        ------
        :exc:`.PagesOutOfRange`
            Given ``page`` does not exist.
        """
        page = int(page)
        if page < 0:
            raise PagesOutOfRange(
                page = page,
                info = 'Page does not support negative integers.'
            )
        if page > self.get_pages_count():
            raise PagesOutOfRange(
                page = page,
                info = self.get_pages_count()
            )
        self._current_page = page

    def view_page(self, page: int = None):
        """View elements on a page.

        Parameters
        ----------
        page: :class:`int`
            If ``page`` is ``None``, returns elements on a current page.
            Otherwise, tries to go to the ``page``, and returns its elements.
            (without switching to that page)

        Raises
        ------
        :exc:`.PagesOutOfRange`
            Raised when given page is out of range.
        """
        if page is None:
            page_to_view = self.get_curr_page()
            to_pass = page_to_view * self.per_page
            res = self.list[to_pass:(to_pass + self.per_page)]
            return res

        else:
            page = int(page)
            if page < 0:
                raise PagesOutOfRange(
                    page = page,
                    info = "Page does not support negative integers."
                )
            if page > self.get_pages_count():
                raise PagesOutOfRange(
                    page = page,
                    info = self.get_pages_count()
                )
            else:
                to_pass = page * self.per_page
                res = self.list[to_pass:(to_pass + self.per_page)]
                return res

    def get_all(self):
        """Pretty similar to self.list, but returns List[List[`Any`]], where each
        inner list represents one page.
        """
        return [self.view_page(i) for i in range(self.get_pages_count())]
