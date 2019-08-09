import asyncio

from .search_utils import find, get
from .wrap_tools import benchmark, check

wait = asyncio.wait  # for less imports outside library


def run(coro, *, debug: bool = False, raise_exceptions: bool = False):
    """Run a _|coroutine_link|.

    This function runs the passed coroutine, taking care
    of the event loop and shutting down asynchronous generators.

    This function is basically ported from Python 3.7 for backwards compability
    with earlier versions of Python.

    This function cannot be called when another event loop is
    running in the same thread.

    If debug is True, the event loop will be run in debug mode.

    This function always creates a new event loop and closes it at the end.
    It should be used as a main entry point to asyncio programs, and should
    ideally be called only once.

    Example: ::
        async def test(pid):
            return pid
        one = gd.utils.run(test(1))

    Parameters
    ----------
    coro: _|coroutine_link|
        Coroutine to run.

    debug: :class:`bool`
        Whether or not to run event loop in debug mode.

    raise_exceptions: :class:`bool`
        Whether to raise errors when shutting down function.

    Returns
    -------
    Any
        Anything that ``coro`` returns.
    """
    
    if asyncio._get_running_loop() is not None:
        raise RuntimeError('Can not perform gd.utils.run() in a running event loop.')

    if not asyncio.iscoroutine(coro):
        raise ValueError(f'A coroutine was expected, got {coro!r}.')

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)
        return loop.run_until_complete(coro)

    finally:
        try:
            _cancel_all_tasks(loop, raise_exceptions=raise_exceptions)
            loop.run_until_complete(loop.shutdown_asyncgens())

        finally:
            asyncio.set_event_loop(None)
            loop.close()


def _cancel_all_tasks(loop, raise_exceptions: bool = False):
    """Cancels all tasks in a loop.

    Returns exceptions if ``raise_exceptions`` is ``True``.

    Parameters
    ----------
    loop: :class:`asyncio.BaseSelectorEventLoop`
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
