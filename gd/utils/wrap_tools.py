import functools
import logging
import time

from ..errors import NotLoggedError

log = logging.getLogger(__name__)

class check:
    
    def is_logged(context):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not context.is_logged():
                    raise NotLoggedError(func.__name__)
                return func(*args, **kwargs)
            return wrapper
        return decorator

#    def is_logged(func):
#        @functools.wraps(func)
#        def wrapper(obj, client, *args, **kwargs):
#            if not client.is_logged():
#                raise NotLoggedError(func.__name__)
#            return func(obj, client, *args, **kwargs)
#        return wrapper

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
