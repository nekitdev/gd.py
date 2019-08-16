import functools
import logging
import time  # not for time.sleep() :)

from ..errors import NotLoggedError, MissingAccess

log = logging.getLogger(__name__)

# |========================================|
# |============= ctypes magic =============|
# |========================================|

import ctypes

def _get_class_dict(cls):
    """Gets 'cls.__dict__' that can be edited."""
    return ctypes.py_object.from_address(id(cls.__dict__) + 16).value

# |======================================|
# |============= Decorators =============|
# |======================================|

class check:

    def is_logged():
        # decorator that checks if passed client is logged in
        def decorator(func):
            @functools.wraps(func)
            def wrapper(obj, *args, **kwargs):

                client = obj if hasattr(obj, 'login') else obj._client

                if client is None:
                    raise MissingAccess(
                        message=(
                            f'Attempt to check if client is logged for {obj} returned None. '
                            'Have you made this object by hand?')
                    )

                if not client.is_logged():
                    raise NotLoggedError(func.__name__)

                return func(obj, *args, **kwargs)

            return wrapper
        return decorator

    def is_logged_obj(obj, func_name):
        client = obj if hasattr(obj, 'login') else obj._client
        if not client.is_logged():
            raise NotLoggedError(func_name)

def benchmark(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):

        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()

        time_taken = (end-start)*1000

        thing = f'Executed "{func.__name__}(*args, **kwargs)"\n' \
            f'Estimated time: {round(time_taken, 2)}ms.'

        log.debug(thing)

        return res
    return decorator


def new_method(cls):
    # decorator that adds new methods to a 'cls'
    def decorator(func):
        cls_d = _get_class_dict(cls)
        cls_d[func.__name__] = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


# |=======================================|
# |============= Other Utils =============|
# |=======================================|


def make_repr(obj, info = {}):
    """Creates a nice __repr__ for the object."""
    module = obj.__module__.split('.')[0]
    name = obj.__class__.__name__

    if not info:
        return f'<{module}.{name}>'

    info = (' '.join('%s=%s' % t for t in info.items()))

    return f'<{module}.{name} {info}>'


def add_method(cls, func, *, name: str = None):
    """Adds a new method to a 'cls'."""
    cls_d = _get_class_dict(cls)

    if name is None:
        name = func.__name__

    cls_d[name] = func
