import ctypes
import functools
import gc
import logging
import time  # not for time.sleep() :)

from ..errors import NotLoggedError, MissingAccess

__all__ = (
    'check', 'benchmark', 'new_method', 'add_method',
    'del_method', 'make_repr', 'find_subclass', 'get_instances_of'
)

log = logging.getLogger(__name__)


def get_class_dict(cls):
    """Gets 'cls.__dict__' that can be edited."""
    return ctypes.py_object.from_address(id(cls.__dict__) + 16).value


class check:
    @classmethod
    def is_logged(cls):
        # decorator that checks if passed client is logged in.
        def decorator(func):
            @functools.wraps(func)
            def wrapper(obj, *args, **kwargs):

                client = obj if hasattr(obj, 'login') else obj._client

                if client is None:
                    raise MissingAccess(
                        message=(
                            'Attempt to check if client is logged for {!r} returned None. '
                            'Have you made this object by hand?').format(obj)
                        )

                if not client.is_logged():
                    raise NotLoggedError(func.__name__)

                return func(obj, *args, **kwargs)

            return wrapper
        return decorator

    @classmethod
    def is_logged_obj(cls, obj, func_name):
        try:
            client = obj if hasattr(obj, 'login') else obj._client

        except AttributeError:
            raise MissingAccess(
                message='None was recieved as an <obj> arg when checking in {!r}.'.format(func_name)
            ) from None

        if not client.is_logged():
            raise NotLoggedError(func_name)


def benchmark(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):

        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()

        time_taken = (end-start)*1000

        thing = (
            'Executed "{}(*args, **kwargs)"\n'
            'Estimated time: {:,.2f}ms.'
        ).format(func.__name__, time_taken)

        log.debug(thing)

        return res
    return decorator


def new_method(cls):
    # decorator that adds new methods to a 'cls'.
    def decorator(func):
        cls_d = get_class_dict(cls)
        cls_d[func.__name__] = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


def make_repr(obj, info = {}):
    """Creates a nice __repr__ for the object."""
    module = obj.__module__.split('.')[0]
    name = obj.__class__.__name__

    if not info:
        return '<{}.{}>'.format(module, name)

    info = (' '.join('%s=%s' % t for t in info.items()))

    return '<{}.{} {}>'.format(module, name, info)


def find_subclass(string_name, superclass=object):
    """Fetches subclass of 'superclass' by 'string_name'."""
    subclasses = {cls.__name__: cls for cls in superclass.__subclasses__()}
    return subclasses.get(string_name, superclass)


def get_instances_of(obj_class=object):
    objects = gc.get_objects()
    return [obj for obj in objects if isinstance(obj, obj_class)]


def del_method(cls, method_name):
    """Delete a method of a 'cls'."""
    cls_d = get_class_dict(cls)
    cls_d.pop(method_name, None)


def add_method(cls, func, *, name: str = None):
    """Adds a new method to a 'cls'."""
    cls_d = get_class_dict(cls)

    if name is None:
        name = func.__name__

    cls_d[name] = func
