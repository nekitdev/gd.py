import functools
import logging
import time  # not for time.sleep() :)

from ..errors import NotLoggedError, MissingAccess

log = logging.getLogger(__name__)

class check:

    def is_logged():
        # decorator that checks if passed client is logged in
        def decorator(func):
            # wrap func so its docstring will be passed accurately
            @functools.wraps(func)
            def wrapper(obj, *args, **kwargs):
                # get client out of object
                client = obj if hasattr(obj, 'login') else obj._client
                if client is None:
                    raise MissingAccess(
                        message=(
                            f'Attempt to check if client is logged for {obj} returned None. '
                            'Have you made this object by hand?')
                    )
                # check if is logged in
                if not client.is_logged():
                    raise NotLoggedError(func.__name__)
                # run function normally
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


def _make_repr(obj, info = {}):
    module = obj.__module__.split('.')[0]
    name = obj.__class__.__name__
    if not info:
        return f'<{module}.{name}>'
    info = (' '.join('%s=%s' % t for t in info.items()))
    return f'<{module}.{name} {info}>'
