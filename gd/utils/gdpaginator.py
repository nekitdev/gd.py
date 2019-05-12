from .errors import error

def paginate(**kwargs):
    return Paginator(**kwargs)

class Paginator:
    def __init__(self, **options):
        self._list = options.get('to_paginate')
        self._per_page = options.get('per_page')
        if ((self._list is None) or (self._per_page is None)):
            raise error.MissingArguments()
        self._length = len(self._list)
        self._elements_per_page = self._per_page
        if not self._elements_per_page > 0:
            raise error.InvalidArgument()
        else:
            if (self._length // self._elements_per_page < self._length / self._elements_per_page):
                self._pages = self._length // self._elements_per_page + 1
            else:
                self._pages = self._length // self._elements_per_page
        self._current_page = 1
        if not self._pages > 0:
            raise error.PaginatorIsEmpty()
    
    def __str__(self):
        return self.get_current_state()

    @property
    def length(self):
        return self._length
    @property
    def per_page(self):
        return self._elements_per_page
    @property
    def list(self):
        return self._list

    def get_pages_count(self):
        return self._pages

    def get_current_page(self):
        return self._current_page

    def has_next_page(self):
        return True if self.get_current_page() < self.get_pages_count() else False

    def has_previous_page(self):
        return True if self.get_current_page() > 1 else False

    def can_run(self):
        return self.length > 0

    def move_to_next(self):
        if not self.has_next_page():
            raise error.PagesOutOfRange(
                page = self.get_current_page() + 1,
                info = self.get_pages_count()
            )
        else:
            self._current_page += 1

    def move_to_previous(self):
        if not self.has_previous_page():
            raise error.PagesOutOfRange(
                page = self.get_current_page() - 1,
                info = 'Page does not support negative integers and zero...'
            )
        else:
            self._current_page -= 1
    
    def move_to(self, **kwargs):
        if len(kwargs) > 1:
            raise error.TooManyArguments()
        if ('page' not in kwargs):
            raise error.MissingArguments()
        page = int(kwargs.get('page'))
        if (abs(page) > page) or (page is 0):
            raise error.PagesOutOfRange(
                page = page,
                info = 'Page does not support negative integers and zero...'
            )
        if page > self.get_pages_count():
            raise error.PagesOutOfRange(
                page = page,
                info = self.get_pages_count()
            )
        else:
            self._current_page = page

    def get_page_elements(self, page: int = None):
        if page is None:
            page_to_view = self.get_current_page() - 1
            to_pass = page_to_view * self.per_page
            res = self.list[to_pass:(to_pass + self.per_page)]
            return res
        else:
            page_to_view = page - 1
            if (abs(page) > page) or (page is 0):
                raise error.PagesOutOfRange(
                    page = page,
                    info = "Page does not support negative integers and zero..."
                )
            if page > self.get_pages_count():
                raise error.PagesOutOfRange(
                    page = page,
                    info = self.get_pages_count()
                )
            else:
                to_pass = page_to_view * self.per_page 
                res = self.list[to_pass:(to_pass + self.per_page)]
                return res

    def get_current_state(self):
        p = self.get_current_page()
        per_page = self.per_page
        return f"""[gd.Paginator]
        [Can Run][{self.can_run()}]
        [Length][{self.length}]
        [Pages][{self.get_pages_count()}]
        [Current State]
        [Page][{self.get_current_page()}]
        [Showing][{((p - 1)*per_page)}/{(p*per_page)} of {self.length}]"""

    def get_everything(self):
        some_dict = {}
        for i in range(self.get_pages_count()):
            some_dict[f'[Page {(i+1)}]'] = self.get_page_elements(i+1)
        return some_dict

#example:
#paginator = gd.Paginator(to_paginate=['15316', '214536'], per_page=1)
#paginator.get_pages_count() //returns '2'
#paginator.get_current_page() //returns '1'
#paginator.move_to(page=2)
#paginator.get_current_page() //returns '2'
#paginator.has_next_page() //returns 'False'
#paginator.get_page_elements() //returns ['214536']
# (._.')/
