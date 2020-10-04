import asyncio
import functools

import inspect

from gd.logging import get_logger
from gd.typing import (
    Awaitable,
    Callable,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)

__all__ = (
    "run_blocking",
    "wait",
    "run",
    "gather",
    "cancel_all_tasks",
    "shutdown_loop",
    "maybe_coroutine",
    "acquire_loop",
)

log = get_logger(__name__)

T = TypeVar("T")


async def run_blocking(func: Callable[..., T], *args, **kwargs) -> T:
    """|coro|

    Run some blocking function in an event loop.

    If there is a running loop, ``func`` is executed in it.

    Otherwise, a new loop is being created and closed at the end of the execution.

    Example:

    .. code-block:: python3

        def make_image() -> Image:
            ...  # long code of creating an image

        # somewhere in an async function:

        image = await run_blocking(make_image)
    """
    loop = acquire_loop(running=True)

    asyncio.set_event_loop(loop)

    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


async def gather(
    *awaitables, loop: Optional[asyncio.AbstractEventLoop] = None, return_exceptions: bool = False,
) -> List[T]:
    """A function that is calling :func:`asyncio.gather`.

    Used for less imports inside and outside gd.py.

    One small addition is that a sequence of awaitables can be given
    as the only positional argument.

    This way, :func:`asyncio.gather` will be run on that sequence.
    """
    if len(awaitables) == 1:
        maybe_awaitables = awaitables[0]

        if not inspect.isawaitable(maybe_awaitables):
            awaitables = maybe_awaitables

    return await asyncio.gather(*awaitables, loop=loop, return_exceptions=return_exceptions)


async def wait(
    *futures,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    timeout: Optional[Union[float, int]] = None,
    return_when: str = "ALL_COMPLETED",
) -> Tuple[Set[asyncio.Future], Set[asyncio.Future]]:
    """A function that is calling :func:`asyncio.wait`.

    Used for less imports inside and outside of this library.

    Wait for the Futures and coroutines given by ``futures`` to complete.

    The sequence futures must not be empty.

    Coroutines will be wrapped in Tasks.

    Returns two sets of Future: (done, pending).

    Usage:

    .. code-block:: python3

        done, pending = await gd.utils.wait(futures)

    .. note::

        This does not raise :exc:`TimeoutError`! Futures that aren't done
        when the timeout occurs are returned in the second set.
    """
    if len(futures) == 1:
        maybe_futures = futures[0]

        if not inspect.isawaitable(maybe_futures):
            futures = maybe_futures

    return await asyncio.wait(futures, loop=loop, timeout=timeout, return_when=return_when)


def run(
    awaitable: Awaitable[T],
    *,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    shutdown: bool = True,
    debug: bool = False,
    set_to_none: bool = False,
) -> T:
    """Run a :ref:`coroutine<coroutine>`.

    This function runs the passed coroutine, taking care
    of the event loop and shutting down asynchronous generators.

    This function is basically ported from Python 3.7 for backwards compability
    with earlier versions of Python.

    This function cannot be called when another event loop is
    running in the same thread.

    If ``debug`` is ``True``, the event loop will be run in debug mode.

    This function creates a new event loop if a ``loop`` is ``None``.
    Loop is closed after the function has finished executing.

    It should be used as a main entry point to asyncio programs, and should
    ideally be called only once.

    Example:

    .. code-block:: python3

        async def return_number(number: int) -> int:
            return number

        one = gd.utils.run(return_number(1))

    Parameters
    ----------
    awaitable: Awaitable[``T``]
        Coroutine to run.

    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        A loop to run ``coro`` with. If ``None`` or omitted, a new event loop is created.

    shutdown: :class:`bool`
        Whether to shut the loop down after running.

    debug: :class:`bool`
        Whether or not to run event loop in debug mode.

    set_to_none: :class:`bool`
        Indicates if the loop should be set to None after execution.

    Returns
    -------
    ``T``
        Whatever the coroutine returns.
    """
    if asyncio._get_running_loop() is not None:
        raise RuntimeError("Can not perform run() in a running event loop.")

    if loop is None:
        loop = asyncio.new_event_loop()

    try:
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)
        return loop.run_until_complete(awaitable)

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

    loop.run_until_complete(gather(to_cancel, loop=loop, return_exceptions=True))

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

    loop.stop()

    try:
        cancel_all_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())

    except Exception as error:
        log.warning(f"{type(error).__name__} was raised. {error}")

    finally:
        loop.close()


async def maybe_coroutine(function: Callable[..., Union[Awaitable[T], T]], *args, **kwargs) -> T:
    value = function(*args, **kwargs)

    if inspect.isawaitable(value):
        return await cast(Awaitable[T], value)

    else:
        return cast(T, value)


def acquire_loop(running: bool = False, enforce_running: bool = False) -> asyncio.AbstractEventLoop:
    """Gracefully acquire a loop.

    The function tries to get an event loop via :func:`asyncio.get_event_loop`.
    On fail, returns a new loop using :func:`asyncio.new_event_loop`.

    Parameters
    ----------
    running: :class:`bool`
        Indicates if the function should get a loop that is already running.

    enforce_running: :class:`bool`
        If ``running`` is ``True``, indicates if :exc:`RuntimeError`
        should be raised if there is no current loop running.
    """
    loop: Optional[asyncio.AbstractEventLoop]

    if running:
        try:
            loop = asyncio._get_running_loop()

        except Exception:  # an error might occur actually
            loop = None

        if loop is not None:
            return loop

        if enforce_running:
            raise RuntimeError("No running event loop.")

    try:
        loop = asyncio.get_event_loop()

        if loop.is_running() and not running:
            # loop is running while we have to get the non-running one,
            # let us raise an error to go into <except> clause.
            raise ValueError("Current event loop is already running.")

        if loop.is_closed():
            # same here, fall into <except> clause if the loop is closed
            raise ValueError("Current event loop is closed.")

    except Exception:
        loop = asyncio.new_event_loop()

    return loop
