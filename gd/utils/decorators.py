import functools
import time

from ..typing import Any, Callable

from ..errors import NotLoggedError, MissingAccess

Function = Callable[[Any], Any]

__all__ = ("check_logged", "check_logged_obj", "benchmark", "run_once")


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
        client = obj if hasattr(obj, "is_logged") else obj.client

    except AttributeError:
        raise MissingAccess(message=f"Failed to find client on object: {obj!r}.") from None

    else:
        if client is None:
            raise MissingAccess(
                message=(
                    f"Attempt to check if client is logged for {obj!r} returned None. "
                    "Have you made this object by hand?"
                )
            )

        if not client.is_logged():
            raise NotLoggedError(func_name)


def benchmark(func: Function) -> Function:
    @functools.wraps(func)
    def decorator(*args, **kwargs) -> Any:

        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()

        time_taken = (end - start) * 1000

        print(f"Executed {func!r}\nEstimated time: {time_taken:,.2f}ms.")

        return res

    return decorator


def run_once(func: Function) -> Function:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        if not hasattr(func, "_res"):
            func._res = func(*args, **kwargs)

        return func._res

    return wrapper
