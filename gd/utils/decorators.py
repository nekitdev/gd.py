import functools
import time

from ..typing import Any, Callable

from ..errors import NotLoggedError, MissingAccess

Function = Callable[[Any], Any]

__all__ = (
    'check_logged', 'check_logged_obj', 'benchmark', 'run_once'
)


def check_logged(func: Function) -> Function:
    # decorator that checks if passed client is logged in.
    @functools.wraps(func)
    def wrapper(obj: Any, *args, **kwargs) -> Any:
        # apply actual check
        check_logged_obj(obj, func.__name__)

        return func(obj, *args, **kwargs)
    return wrapper


def check_logged_obj(obj: Any, func_name: str) -> None:
    try:
        client = obj if hasattr(obj, 'is_logged') else obj._client

    except AttributeError:
        raise MissingAccess(
            message='Failed to find client on object: {!r}.'.format(obj)
        ) from None

    else:
        if client is None:
            raise MissingAccess(
                message=(
                    'Attempt to check if client is logged for {!r} returned None. '
                    'Have you made this object by hand?'
                ).format(obj)
            )

        if not client.is_logged():
            raise NotLoggedError(func_name)


def benchmark(func: Function) -> Function:
    @functools.wraps(func)
    def decorator(*args, **kwargs) -> Any:

        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()

        time_taken = (end-start)*1000

        thing = (
            'Executed {0!r}\n'
            'Estimated time: {1:,.2f}ms.'
        ).format(func, time_taken)

        print(thing)

        return res
    return decorator


def run_once(func: Function) -> Function:

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        if not hasattr(func, '_res'):
            func._res = func(*args, **kwargs)

        return func._res

    return wrapper
