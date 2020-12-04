"""discord.py task implementation, adjusted for gd.py.

The MIT License (MIT)

Copyright (c) 2015-2020 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
import inspect
import random
import time

import aiohttp

from gd.async_utils import get_maybe_running_loop
from gd.errors import GDException
from gd.logging import get_logger
from gd.typing import Awaitable, Callable, Optional, Tuple, Type, TypeVar, Union

__all__ = ("ExponentialBackoff", "Loop", "loop")

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")

MAX_ASYNCIO_SECONDS = 3456000

log = get_logger(__name__)


class ExponentialBackoff:
    """An implementation of the exponential backoff algorithm.

    Provides a convenient interface to implement an exponential backoff
    for reconnecting or retrying transmissions in a distributed network.

    Once instantiated, the delay method will return the next interval to
    wait for when retrying a connection or transmission.  The maximum
    delay increases exponentially with each retry up to a maximum of
    2^10 * base, and is reset if no more attempts are needed in a period
    of 2^11 * base seconds.

    Parameters
    ----------
    base: :class:`int`
        The base delay in seconds. The first retry-delay will be up to
        this many seconds.

    integral: :class:`bool`
        Set to ``True`` if whole periods of base is desirable, otherwise any
        number in between may be returned.
    """

    def __init__(self, base: int = 1, *, integral: bool = False) -> None:
        self._base = base

        self._exp = 0
        self._max = 10
        self._reset_time = base * 2 ** 11
        self._last_invocation = time.monotonic()

        # Use our own random instance to avoid messing with global one
        random_object = random.Random()
        random_object.seed()

        self._randfunc: Union[Callable[[int, int], int], Callable[[float, float], float]] = (
            random_object.randrange if integral else random_object.uniform
        )

    def delay(self) -> Union[float, int]:
        """Compute the next delay.

        Returns the next delay to wait according to the exponential
        backoff algorithm.  This is a value between 0 and base * 2^exp
        where exponent starts off at 1 and is incremented at every
        invocation of this method up to a maximum of 10.

        If a period of more than base * 2^11 has passed since the last
        retry, the exponent is reset to 1.
        """
        invocation = time.monotonic()
        interval = invocation - self._last_invocation
        self._last_invocation = invocation

        if interval > self._reset_time:
            self._exp = 0

        self._exp = min(self._exp + 1, self._max)
        return self._randfunc(0, self._base * 2 ** self._exp)


class Loop:
    """A background task helper that abstracts the loop and reconnection logic for you.

    The main interface to create this is through :func:`~gd.tasks.loop`.
    """

    def __init__(
        self,
        seconds: Union[float, int],
        hours: Union[float, int],
        minutes: Union[float, int],
        coroutine: Callable[..., Awaitable[T]],
        count: Optional[int],
        reconnect: bool,
        loop: Optional[asyncio.AbstractEventLoop],
    ) -> None:
        self.coroutine = coroutine
        self.reconnect = reconnect
        self.loop = loop or get_maybe_running_loop()
        self.count = count

        self._current_loop = 0
        self._injected: Optional[S] = None  # type: ignore
        self._task: Optional[asyncio.Task] = None
        self._valid_exception: Tuple[Type[BaseException], ...] = (
            OSError,
            GDException,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        )

        self._before_loop: Optional[Callable[..., Awaitable[T]]] = None
        self._after_loop: Optional[Callable[..., Awaitable[T]]] = None
        self._is_being_cancelled = False
        self._has_failed = False
        self._stop_next_iteration = False

        if self.count is not None and self.count <= 0:
            raise ValueError("Count must be greater than 0 or None.")

        self.change_interval(seconds=seconds, minutes=minutes, hours=hours)

        if not inspect.iscoroutinefunction(self.coroutine):
            raise TypeError(f"Expected coroutine function, not {type(self.coroutine).__name__!r}.")

    async def _call_loop_function(self, name: str) -> None:
        coroutine = getattr(self, "_" + name)

        if coroutine is None:
            return

        if self._injected is not None:
            await coroutine(self._injected)

        else:
            await coroutine()

    async def _loop(self, *args, **kwargs) -> None:
        backoff = ExponentialBackoff()

        await self._call_loop_function("before_loop")

        try:
            while True:
                try:
                    await self.coroutine(*args, **kwargs)

                except self._valid_exception:

                    if not self.reconnect:
                        raise

                    await asyncio.sleep(backoff.delay())

                else:
                    if self._stop_next_iteration:
                        return

                    self._current_loop += 1

                    if self._current_loop == self.count:
                        break

                    await asyncio.sleep(self._sleep)

        except asyncio.CancelledError:
            self._is_being_cancelled = True
            raise

        except Exception:
            self._has_failed = True
            log.exception("Internal background task failed.")
            raise

        finally:
            await self._call_loop_function("after_loop")

            self._is_being_cancelled = False
            self._current_loop = 0
            self._stop_next_iteration = False
            self._has_failed = False

    def __get__(self, self_object: Optional[S], object_type: Type[S]) -> "Loop":
        if self_object is None:
            return self

        self._injected = self_object

        return self

    @property
    def current_loop(self) -> int:
        """:class:`int`: The current iteration of the loop."""
        return self._current_loop

    def start(self, *args, **kwargs) -> asyncio.Task:
        r"""Starts the internal task in the event loop.

        Parameters
        ----------
        \*args
            The arguments to to use.
        \*\*kwargs
            The keyword arguments to use.

        Raises
        ------
        :exc:`RuntimeError`
            A task has already been launched and is running.

        Returns
        -------
        :class:`asyncio.Task`
            The task that has been created.
        """

        if self._task is not None and not self._task.done():
            raise RuntimeError("Task is already launched and is not completed.")

        if self._injected is not None:
            args = (self._injected, *args)

        self._task = self.loop.create_task(self._loop(*args, **kwargs))

        return self._task

    def stop(self) -> None:
        r"""Gracefully stops the task from running.

        Unlike :meth:`~gd.tasks.Loop.cancel`, this allows the task to finish its
        current iteration before gracefully exiting.

        .. note::

            If the internal function raises an error that can be
            handled before finishing then it will retry until
            it succeeds.

            If this is undesirable, either remove the error handling
            before stopping via :meth:`~gd.tasks.Loop.clear_exception_types` or
            use :meth:`~gd.tasks.Loop.cancel` instead.
        """
        if self._task is not None and not self._task.done():
            self._stop_next_iteration = True

    def _can_be_cancelled(self) -> bool:
        return not self._is_being_cancelled and self._task is not None and not self._task.done()

    def cancel(self) -> None:
        """Cancels the internal task, if it is running."""
        if self._can_be_cancelled():
            self._task.cancel()  # type: ignore

    def restart(self, *args, **kwargs) -> None:
        r"""A convenient method to restart the internal task.

        .. note::

            Due to the way this function works, the task is not
            returned like :meth:`~gd.tasks.Loop.start`.

        Parameters
        ------------
        \*args
            The arguments to to use.
        \*\*kwargs
            The keyword arguments to use.
        """

        def restart_when_over(
            future: Union[asyncio.Future, asyncio.Task], *, args=args, kwargs=kwargs
        ) -> None:
            self._task.remove_done_callback(restart_when_over)  # type: ignore
            self.start(*args, **kwargs)

        if self._can_be_cancelled():
            self._task.add_done_callback(restart_when_over)  # type: ignore
            self._task.cancel()  # type: ignore

    def add_exception_type(self, exception: Type[BaseException]) -> None:
        r"""Adds an exception type to be handled during the reconnect logic.

        This function is useful if you're interacting with a 3rd party library that
        raises its own set of exceptions.

        Parameters
        ------------
        exc: Type[:class:`BaseException`]
            The exception class to handle.

        Raises
        --------
        :exc:`TypeError`
            The exception passed is either not a class or not inherited from :class:`BaseException`.
        """
        if not inspect.isclass(exception):
            raise TypeError(f"{exception!r} must be a class.")

        if not issubclass(exception, BaseException):
            raise TypeError(f"{exception!r} must inherit from BaseException.")

        self._valid_exception = (*self._valid_exception, exception)

    def clear_exception_types(self) -> None:
        """Removes all exception types that are handled.

        .. note::

            This operation obviously cannot be undone!
        """
        self._valid_exception = tuple()

    def remove_exception_type(self, exception: Type[BaseException]) -> bool:
        """Removes an exception type from being handled during the reconnect logic.

        Parameters
        ------------
        exc: Type[:class:`BaseException`]
            The exception class to handle.

        Returns
        ---------
        :class:`bool`
            Whether it was successfully removed.
        """
        old_length = len(self._valid_exception)

        self._valid_exception = tuple(
            valid_exception
            for valid_exception in self._valid_exception
            if valid_exception is not exception
        )

        return len(self._valid_exception) != old_length

    def get_task(self) -> Optional[asyncio.Task]:
        """Optional[:class:`asyncio.Task`]: Fetches the internal task or
        ``None`` if there isn't one running.
        """
        return self._task

    def is_being_cancelled(self) -> bool:
        """Whether the task is being cancelled."""
        return self._is_being_cancelled

    def failed(self) -> bool:
        """:class:`bool`: Whether the internal task has failed."""
        return self._has_failed

    def before_loop(self, coroutine: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """A decorator that registers a coroutine to be called before the loop starts running.

        The coroutine must take no arguments (except ``self`` in a class context).

        Parameters
        ------------
        coroutine: :ref:`coroutine <coroutine>`
            The coroutine to register before the loop runs.

        Raises
        -------
        :exc:`TypeError`
            The function was not a coroutine.
        """

        if not inspect.iscoroutinefunction(coroutine):
            raise TypeError(f"Expected coroutine function, received {type(coroutine).__name__!r}.")

        self._before_loop = coroutine
        return coroutine

    def after_loop(self, coroutine: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        """A decorator that register a coroutine to be called after the loop finished running.

        The coroutine must take no arguments (except ``self`` in a class context).

        .. note::

            This coroutine is called even during cancellation. If it is desirable
            to tell apart whether something was cancelled or not, check to see
            whether :meth:`~gd.tasks.Loop.is_being_cancelled` is ``True`` or not.

        Parameters
        ------------
        coroutine: :ref:`coroutine <coroutine>`
            The coroutine to register after the loop finishes.

        Raises
        -------
        :exc:`TypeError`
            The function was not a coroutine.
        """

        if not inspect.iscoroutinefunction(coroutine):
            raise TypeError(f"Expected coroutine function, received {type(coroutine).__name__!r}.")

        self._after_loop = coroutine
        return coroutine

    def change_interval(
        self,
        *,
        seconds: Union[float, int] = 0,
        minutes: Union[float, int] = 0,
        hours: Union[float, int] = 0,
    ) -> None:
        """Changes the interval for the sleep time.

        .. note::

            This only applies on the next loop iteration.
            If it is desirable for the change of interval
            to be applied right away, cancel the task with :meth:`~gd.tasks.Loop.cancel`.

        Parameters
        ------------
        seconds: :class:`float`
            The number of seconds between every iteration.

        minutes: :class:`float`
            The number of minutes between every iteration.

        hours: :class:`float`
            The number of hours between every iteration.

        Raises
        -------
        :exc:`ValueError`
            An invalid value was given.
        """

        sleep = seconds + (minutes * 60.0) + (hours * 3600.0)

        if sleep >= MAX_ASYNCIO_SECONDS:
            raise ValueError(
                f"Total number of seconds exceeds asyncio limit of {MAX_ASYNCIO_SECONDS} seconds."
            )

        if sleep < 0:
            raise ValueError("Total number of seconds cannot be less than zero.")

        self._sleep = sleep

        self.seconds = seconds
        self.hours = hours
        self.minutes = minutes


def loop(
    *,
    seconds: Union[float, int] = 0,
    minutes: Union[float, int] = 0,
    hours: Union[float, int] = 0,
    count: Optional[int] = None,
    reconnect: bool = True,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> Callable[[Callable[..., Awaitable[T]]], Loop]:
    """A decorator that schedules a task in the background for you with
    optional reconnect logic.

    Parameters
    ------------
    seconds: :class:`float`
        The number of seconds between every iteration.

    minutes: :class:`float`
        The number of minutes between every iteration.

    hours: :class:`float`
        The number of hours between every iteration.

    count: Optional[:class:`int`]
        The number of loops to do, ``None`` if it should be an
        infinite loop.

    reconnect: :class:`bool`
        Whether to handle errors and restart the task
        using an exponential back-off algorithm.

    loop: :class:`asyncio.AbstractEventLoop`
        The loop to use to register the task, if not given
        defaults to :func:`asyncio.get_event_loop`.

    Raises
    --------
    :exc:`ValueError`
        An invalid value was given.

    :exc:`TypeError`
        The function was not a coroutine.

    Returns
    -------
    :class:`~gd.tasks.Loop`
        The loop helper that handles the background task.
    """

    def decorator(function: Callable[..., Awaitable[T]]) -> Loop:
        return Loop(
            coroutine=function,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            count=count,
            reconnect=reconnect,
            loop=loop,
        )

    return decorator
