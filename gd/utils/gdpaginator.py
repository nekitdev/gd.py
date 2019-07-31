from ..errors import PaginatorIsEmpty, PagesOutOfRange
from .wrap_tools import _make_repr

def paginate(iterable, per_page: int = 10):
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
        self._length = len(self._list)
        self._configure_pages()
        self._current_page = 0
        if not self._pages > 0:
            raise PaginatorIsEmpty()

    def _configure_pages(self):
        if (self._length // self._per_page < self._length / self._per_page):
            self._pages = self._length // self._per_page + 1
        else:
            self._pages = self._length // self._per_page
    
    def __str__(self):
        return self.get_current_state()
    
    def __repr__(self):
        info = {
            'can_run': self.can_run(),
            'length': self.length,
            'per_page': self.per_page,
            'pages': self.get_pages_count(),
            'current': self.get_current_page()
        }
        return _make_repr(self, info)

    @property
    def length(self):
        return self._length

    @property
    def per_page(self):
        return self._per_page

    @property
    def list(self):
        return self._list
    
    def reload(self):
        self._length = len(self._list)
        self._configure_pages()

    def append(self, obj):
        self._list.append(obj)
        self.reload()
    
    def pop(self, index = None):
        popped_val = None
        if index is None:
            popped_val = self._list.pop()
        else:
            del self._list[index]
        self.reload()
        if self._length == 0:
            raise error.PaginatorIsEmpty()
        return popped_val

    def get_pages_count(self):
        return self._pages

    def get_current_page(self):
        return self._current_page

    def has_next_page(self):
        return True if self.get_current_page() < self.get_pages_count() else False

    def has_previous_page(self):
        return True if self.get_current_page() > 0 else False

    def can_run(self):
        return self.length > 0

    def move_to_next(self):
        if not self.has_next_page():
            raise error.PagesOutOfRange(
                page = self.get_current_page() + 1,
                info = self.get_pages_count()
            )
        self._current_page += 1

    def move_to_previous(self):
        if not self.has_previous_page():
            raise error.PagesOutOfRange(
                page = self.get_current_page() - 1,
                info = 'Page does not support negative integers.'
            )
        self._current_page -= 1
    
    def move_to(self, page):
        page = int(page)
        if abs(page) > page:
            raise error.PagesOutOfRange(
                page = page,
                info = 'Page does not support negative integers.'
            )
        if page > self.get_pages_count():
            raise error.PagesOutOfRange(
                page = page,
                info = self.get_pages_count()
            )
        self._current_page = page

    def view_page(self, page: int = None):
        if page is None:
            page_to_view = self.get_current_page()
            to_pass = page_to_view * self.per_page
            res = self.list[to_pass:(to_pass + self.per_page)]
            return res
        else:
            if abs(page) > page:
                raise error.PagesOutOfRange(
                    page = page,
                    info = "Page does not support negative integers."
                )
            if page > self.get_pages_count():
                raise error.PagesOutOfRange(
                    page = page,
                    info = self.get_pages_count()
                )
            else:
                to_pass = page * self.per_page 
                res = self.list[to_pass:(to_pass + self.per_page)]
                return res

    def get_current_state(self):
        p = self.get_current_page()
        per_page = self.per_page
        return f'[gd.Paginator]\n[Can_Run:{self.can_run()}]\n' \
            f'[Length:{self.length}]\n[Pages:{self.get_pages_count()}]\n' \
            f'[Current_State]\n[Page:{self.get_current_page()}]\n' \
            f'[Showing:{(p*per_page)}/{((p+1)*per_page)} of {self.length}]'

    def get_all(self):
        for i in range(self.get_pages_count()):
            yield self.view_page(i+1)

# TO_DO: make documentation
