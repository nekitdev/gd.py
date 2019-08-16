import asyncio

from .enums import value_to_enum
from .search_utils import find, get
from .wrap_tools import benchmark, check

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
    except Exception as error:  # failed to convert
        try:
            return on_fail_type(obj)
        except Exception as error:
            return obj


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
    return await asyncio.wait(fs, loop=loop, timeout=timeout, return_when=return_when)


def run(coro, *, loop=None, debug: bool = False, raise_exceptions: bool = False):
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

    raise_exceptions: :class:`bool`
        Whether to raise errors when shutting down function.

    Returns
    -------
    `Any`
        Anything that ``coro`` returns.
    """
    
    if asyncio._get_running_loop() is not None:
        raise RuntimeError('Can not perform gd.utils.run() in a running event loop.')

    if not asyncio.iscoroutine(coro):
        raise ValueError(f'A coroutine was expected, got {coro!r}.')

    if loop is not None:
        return loop.run_until_complete(coro)

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)
        return loop.run_until_complete(coro)

    finally:
        try:
            cancel_all_tasks(loop, raise_exceptions=raise_exceptions)
            loop.run_until_complete(loop.shutdown_asyncgens())

        finally:
            asyncio.set_event_loop(None)
            loop.close()


def cancel_all_tasks(loop, raise_exceptions: bool = False):
    """Cancels all tasks in a loop.

    Returns exceptions if ``raise_exceptions`` is ``True``.

    Parameters
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        Event loop to cancel tasks in.

    raise_exceptions: :class:`bool`
        Indicates if exceptions should be raised.
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
        asyncio.gather(*to_cancel, loop=loop, return_exceptions=raise_exceptions)
    )

    for task in to_cancel:
        if task.cancelled():
            continue

        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during gd.utils.run() shutdown',
                'exception': task.exception(),
                'task': task,
            })
