import functools
import gc
import logging
import time

from ..errors import NotLoggedError, MissingAccess

__all__ = (
    'check', 'benchmark', 'new_method', 'add_method', 'del_method',
    'make_repr', 'find_subclass', 'get_instances_of', 'find_objects',
    'run_once', 'convert_to_type', 'get_class_dict',
)

log = logging.getLogger(__name__)


def get_class_dict(cls):
    """Gets 'cls.__dict__' that can be edited."""
    for obj in gc.get_objects():

        try:
            if obj == dict(cls.__dict__) and type(obj) is dict:
                return obj

        except Exception:
            continue

    raise ValueError(
        'Failed to find editable __dict__ for {}.'.format(cls)
    )


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
                            'Have you made this object by hand?'
                        ).format(obj)
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


def new_method(cls, *, name: str = None):
    # decorator that adds new methods to a 'cls'.
    def decorator(func):
        f_name = name or _get_name(func)

        cls_d = get_class_dict(cls)
        cls_d[f_name] = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


def run_once(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        if not hasattr(func, '_res'):
            func._res = func(*args, **kwargs)

        return func._res

    return wrapper


def make_repr(obj, info: dict = None):
    """Creates a nice __repr__ for the object."""
    if info is None:
        info = {}

    module = obj.__module__.split('.')[0]
    name = obj.__class__.__name__

    if not info:
        return '<{}.{}>'.format(module, name)

    info = (' '.join('%s=%s' % t for t in info.items()))

    return '<{}.{} {}>'.format(module, name, info)


def convert_to_type(obj: object, try_type: type, on_fail_type: type = None):
    """A function that tries to convert the given object to a provided type

    Parameters
    ----------
    obj: :class:`object`
        Any object to convert into given type.

    try_type: :class:`type`
        Type to convert an object to.

    on_fail_type: :class:`type`
        Type to convert an object on fail.
        If ``None`` or omitted, returns an ``obj``.
        On fail returns ``obj`` as well.

    Returns
    -------
    `Any`
        Object of given ``try_type``, on fail of type ``on_fail_type``, and
        ``obj`` if ``on_fail_type`` is ``None`` or failed to convert.
    """
    try:
        return try_type(obj)
    except Exception:  # failed to convert
        try:
            return on_fail_type(obj)
        except Exception:
            return obj


def find_subclass(string_name, superclass=object):
    """Fetches subclass of 'superclass' by 'string_name'."""
    subclasses = {cls.__name__: cls for cls in superclass.__subclasses__()}
    return subclasses.get(string_name, superclass)


def get_instances_of(obj_class=object):
    predicate = lambda obj: isinstance(obj, obj_class)

    return find_objects(predicate)


def find_objects(predicate=None):
    if predicate is None:
        return list()

    objects = gc.get_objects()

    return list(filter(predicate, objects))


def del_method(cls, method_name):
    """Delete a method of a 'cls'."""
    cls_d = get_class_dict(cls)
    cls_d.pop(method_name, None)


def add_method(cls, func, *, name: str = None):
    """Adds a new method to a 'cls'."""
    cls_d = get_class_dict(cls)

    if name is None:
        name = _get_name(func)

    cls_d[name] = func


def _get_name(func):
    try:
        if isinstance(func, property):
            return func.fget.__name__
        elif isinstance(func, (staticmethod, classmethod)):
            return func.__func__.__name__
        else:
            return func.__name__
    except AttributeError:
        raise RuntimeError('Failed to find the name of given function. Please provide the name explicitly.') from None
