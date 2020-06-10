import asyncio
import functools

import inspect

from gd.logging import get_logger
from gd.typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

__all__ = (
    "run_blocking_io",
    "wait",
    "run",
    "gather",
    "cancel_all_tasks",
    "shutdown_loop",
    "maybe_coroutine",
    "acquire_loop",
    "aiter",
    "anext",
)

log = get_logger("gd.async")


async def run_blocking_io(func: Callable, *args, **kwargs) -> Any:
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


async def gather(
    *aws: Sequence[Awaitable],
    loop: Optional[asyncio.AbstractEventLoop] = None,
    return_exceptions: bool = False,
) -> List[Any]:
    """A function that is calling :func:`asyncio.gather`.

    Used for less imports inside and outside gd.py.

    One small addition is that a sequence of awaitables can be given
    as the only positional argument.

    This way, :func:`asyncio.gather` will be run on that sequence.
    """
    if len(aws) == 1:
        maybe_aw = aws[0]
        if not inspect.isawaitable(maybe_aw):
            aws = maybe_aw

    return await asyncio.gather(*aws, loop=loop, return_exceptions=return_exceptions)


async def wait(
    *fs: Iterable[Coroutine],
    loop: Optional[asyncio.AbstractEventLoop] = None,
    timeout: Optional[Union[float, int]] = None,
    return_when: str = "ALL_COMPLETED",
) -> Tuple[Set[asyncio.Future], Set[asyncio.Future]]:
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
    if len(fs) == 1:
        maybe_aw = fs[0]
        if not inspect.isawaitable(maybe_aw):
            fs = maybe_aw

    return await asyncio.wait(fs, loop=loop, timeout=timeout, return_when=return_when)


def run(
    coro: Coroutine,
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    debug: bool = False,
    set_to_none: bool = False,
) -> Any:
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
        raise RuntimeError("Can not perform gd.utils.run() in a running event loop.")

    if not asyncio.iscoroutine(coro):
        raise ValueError(f"A coroutine was expected, got {coro!r}.")

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


def cancel_all_tasks(loop: asyncio.AbstractEventLoop) -> None:
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

    loop.run_until_complete(asyncio.gather(*to_cancel, loop=loop, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue

        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during runner shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def shutdown_loop(loop: asyncio.AbstractEventLoop) -> None:
    if loop.is_closed():
        return

    try:
        cancel_all_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())

    except Exception as exc:
        log.warning(f"Error<{type(exc).__name__}> was raised. {exc}")

    finally:
        loop.close()


async def maybe_coroutine(func: Callable, *args, **kwargs) -> Any:
    value = func(*args, **kwargs)

    if inspect.isawaitable(value):
        return await value

    else:
        return value


def acquire_loop(running: bool = False) -> asyncio.AbstractEventLoop:
    """Gracefully acquire a loop.

    The function tries to get an event loop via :func:`asyncio.get_event_loop`.
    On fail, returns a new loop using :func:`asyncio.new_event_loop`.

    Parameters
    ----------
    running: :class:`bool`
        Indicates if the function should get a loop that is already running.
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

            if loop.is_running() and not running:
                # loop is running while we have to get the non-running one,
                # let us raise an error to go into <except> clause.
                raise ValueError("Current event loop is already running.")

        except Exception:
            loop = asyncio.new_event_loop()

    return loop


async def aiter(some_object: Any) -> Any:
    return await some_object.__aiter__()


async def anext(async_generator: Any) -> Any:
    return await async_generator.__anext__()
