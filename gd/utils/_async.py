import asyncio
import functools
import inspect

from .wrap_tools import find_subclass, add_method, del_method

__all__ = (
    'run_blocking_io', 'wait', 'run', 'sync',
    'cancel_all_tasks', 'shutdown_loop',
    'coroutine', 'maybe_coroutine', 'acquire_loop',
    'enable_asyncwrap', 'enable_run_method', 'synchronize'
)

coroutine = find_subclass('coroutine')


async def run_blocking_io(func, *args, **kwargs):
    """|coro|

    Run some blocking function in an event loop.

    If there is a running loop, ``'func'`` is executed in it.

    Otherwise, a new loop is being created and closed at the end of the execution.

    Example:

    .. code-block:: python3

        def make_image():
            ...  # long code of creating an image

        # somewhere in an async function:

        await run_blocking_io(make_image)
    """
    loop = acquire_loop(running=True)

    asyncio.set_event_loop(loop)

    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


async def wait(fs, *, loop=None, timeout=None, return_when='ALL_COMPLETED'):
    """A function that is calling :func:`asyncio.wait`.

    Used for less imports inside and outside of this library.

    Wait for the Futures and coroutines given by fs to complete.

    The sequence futures must not be empty.

    Coroutines will be wrapped in Tasks.

    Returns two sets of Future: (done, pending).

    Usage:

    .. code-block:: python3

        done, pending = await gd.utils.wait(fs)

    .. note::

        This does not raise :exc:`TimeoutError`! Futures that aren't done
        when the timeout occurs are returned in the second set.
    """
    try:
        if loop is None:
            loop = acquire_loop()
        fs = set(fs)

    except TypeError:  # not iterable 'fs'
        fs = {fs}

    fs = {asyncio.ensure_future(f, loop=loop) for f in fs}

    return await asyncio.wait(fs, loop=loop, timeout=timeout, return_when=return_when)


def run(coro, *, loop=None, debug: bool = False, set_to_none: bool = False):
    """Run a |coroutine_link|_.

    This function runs the passed coroutine, taking care
    of the event loop and shutting down asynchronous generators.

    This function is basically ported from Python 3.7 for backwards compability
    with earlier versions of Python.

    This function cannot be called when another event loop is
    running in the same thread.

    If ``debug`` is ``True``, the event loop will be run in debug mode.

    This function creates a new event loop and closes it at the end if a ``loop`` is ``None``.

    If a loop is given, this function basically calls :meth:`asyncio.AbstractEventLoop.run_until_complete`.

    It should be used as a main entry point to asyncio programs, and should
    ideally be called only once.

    Example:

    .. code-block:: python3

        async def test(pid):
            return pid

        one = gd.utils.run(test(1))

    Parameters
    ----------
    coro: |coroutine_link|_
        Coroutine to run.

    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        A loop to run ``coro`` with. If ``None`` or omitted, a new event loop is created.

    debug: :class:`bool`
        Whether or not to run event loop in debug mode.

    set_to_none: :class:`bool`
        Indicates if the loop should be set to None after execution.

    Returns
    -------
    `Any`
        Anything that ``coro`` returns.
    """

    if asyncio._get_running_loop() is not None:
        raise RuntimeError('Can not perform gd.utils.run() in a running event loop.')

    if not asyncio.iscoroutine(coro):
        raise ValueError('A coroutine was expected, got {!r}.'.format(coro))

    shutdown = False

    if loop is None:
        loop = asyncio.new_event_loop()
        shutdown = True

    try:
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)
        return loop.run_until_complete(coro)

    finally:
        if shutdown:
            shutdown_loop(loop)

        if set_to_none:
            loop = None

        else:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)


def cancel_all_tasks(loop):
    """Cancels all tasks in a loop.

    Parameters
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        Event loop to cancel tasks in.
    """
    try:
        to_cancel = asyncio.all_tasks(loop)
    except AttributeError:  # py < 3.7
        to_cancel = asyncio.Task.all_tasks(loop)

    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=True)
    )

    for task in to_cancel:
        if task.cancelled():
            continue

        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during runner shutdown',
                'exception': task.exception(),
                'task': task
            })


def shutdown_loop(loop, set_event_loop_to_none: bool = False):
    try:
        cancel_all_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())

    finally:
        if set_event_loop_to_none:
            asyncio.set_event_loop(None)

        loop.close()


async def maybe_coroutine(func, *args, **kwargs):
    value = func(*args, **kwargs)
    if inspect.isawaitable(value):
        return await value
    else:
        return value


def acquire_loop(running: bool = False):
    """Gracefully acquire a loop.

    The function tries to get an event loop via :func:`asyncio.get_event_loop`.
    On fail, returns a new loop using :func:`asyncio.new_event_loop`.

    Parameters
    ----------
    running: :class:`bool`
        Indicates if the function should get a loop that is already running. (on fail, the main get process is being executed.)
    """
    try:
        loop = asyncio._get_running_loop()

    except Exception:  # an error might occur actually
        loop = None

    if running and loop is not None:
        return loop

    else:
        try:
            loop = asyncio.get_event_loop()

        except Exception:
            loop = asyncio.new_event_loop()

    return loop


def sync(loop=None):
    if loop is None:
        loop = acquire_loop()

    def decorator(func):
        f_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            coro = maybe_coroutine(func, *args, **kwargs)
            return loop.run_until_complete(coro)

        env = {'wrapper': wrapper}

        exec('def {}(*args, **kwargs): return wrapper(*args, **kwargs)'.format(f_name), env)

        inner = env.get(f_name)

        return inner
    return decorator


def _run(self, loop=None):
    """Run the coroutine in a new event loop,
    closing the loop after execution (if not given).
    """

    if loop is None:
        loop = acquire_loop()

    asyncio.set_event_loop(loop)

    return loop.run_until_complete(self)


async def _async_wrapper(var):
    try:
        return await var
    except Exception:
        return var

def _asyncwrap(self):
    return _async_wrapper(self)


def _enable_method(obj: type, name: str, on: bool = True, func=None):
    try:
        if on:
            add_method(obj, func, name=name)
        else:
            del_method(obj, name)

    except Exception:
        print('Failed to edit the {!r} method.'.format(name))

def enable_asyncwrap(on: bool = True):
    """Add or delete '__asyncwrap__' method of objects."""
    _enable_method(object, '__asyncwrap__', on, _asyncwrap)


def enable_run_method(on: bool = True):
    """Add or delete 'run' method of a coroutine."""
    _enable_method(coroutine, 'run', on, _run)


def synchronize(on: bool = True):
    enable_asyncwrap(on)
    enable_run_method(on)
