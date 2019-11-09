# This is pretty much a copy of discord.py implementation.

import asyncio
import aiohttp
import gd
import inspect
import logging
import random
import time

MAX_ASYNCIO_SECONDS = 3456000

log = logging.getLogger(__name__)

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

    def __init__(self, base=1, *, integral=False):
        self._base = base

        self._exp = 0
        self._max = 10
        self._reset_time = base * 2 ** 11
        self._last_invocation = time.monotonic()

        # Use our own random instance to avoid messing with global one
        rand = random.Random()
        rand.seed()

        self._randfunc = rand.randrange if integral else rand.uniform

    def delay(self):
        """Compute the next delay

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

    The main interface to create this is through :func:`loop`.
    """
    def __init__(self, coro, seconds, hours, minutes, count, reconnect, loop):
        self.coro = coro
        self.reconnect = reconnect
        self.loop = loop or asyncio.get_event_loop()
        self.count = count
        self._current_loop = 0
        self._task = None
        self._injected = None
        self._valid_exception = (
            OSError,
            gd.ClientException,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        )

        self._before_loop = None
        self._after_loop = None
        self._is_being_cancelled = False
        self._has_failed = False
        self._stop_next_iteration = False

        if self.count is not None and self.count <= 0:
            raise ValueError('Count must be greater than 0 or None.')

        self.change_interval(seconds=seconds, minutes=minutes, hours=hours)

        if not inspect.iscoroutinefunction(self.coro):
            raise TypeError('Expected coroutine function, not {!r}.'.format(type(self.coro).__name__))

    async def _call_loop_function(self, name):
        coro = getattr(self, '_' + name)
        if coro is None:
            return

        if self._injected is not None:
            await coro(self._injected)
        else:
            await coro()

    async def _loop(self, *args, **kwargs):
        backoff = ExponentialBackoff()
        await self._call_loop_function('before_loop')
        try:
            while True:
                try:
                    await self.coro(*args, **kwargs)
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
            log.exception('Internal background task failed.')
            raise
        finally:
            await self._call_loop_function('after_loop')
            self._is_being_cancelled = False
            self._current_loop = 0
            self._stop_next_iteration = False
            self._has_failed = False

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        self._injected = obj
        return self

    @property
    def current_loop(self):
        """:class:`int`: The current iteration of the loop."""
        return self._current_loop

    def start(self, *args, **kwargs):
        r"""Starts the internal task in the event loop.

        Parameters
        ------------
        \*args
            The arguments to to use.
        \*\*kwargs
            The keyword arguments to use.

        Raises
        --------
        RuntimeError
            A task has already been launched and is running.

        Returns
        ---------
        :class:`asyncio.Task`
            The task that has been created.
        """

        if self._task is not None and not self._task.done():
            raise RuntimeError('Task is already launched and is not completed.')

        if self._injected is not None:
            args = (self._injected, *args)

        self._task = self.loop.create_task(self._loop(*args, **kwargs))
        return self._task

    def stop(self):
        r"""Gracefully stops the task from running.

        Unlike :meth:`cancel`\, this allows the task to finish its
        current iteration before gracefully exiting.

        .. note::

            If the internal function raises an error that can be
            handled before finishing then it will retry until
            it succeeds.

            If this is undesirable, either remove the error handling
            before stopping via :meth:`clear_exception_types` or
            use :meth:`cancel` instead.
        """
        if self._task and not self._task.done():
            self._stop_next_iteration = True

    def _can_be_cancelled(self):
        return not self._is_being_cancelled and self._task and not self._task.done()

    def cancel(self):
        """Cancels the internal task, if it is running."""
        if self._can_be_cancelled():
            self._task.cancel()

    def restart(self, *args, **kwargs):
        r"""A convenience method to restart the internal task.

        .. note::

            Due to the way this function works, the task is not
            returned like :meth:`start`.

        Parameters
        ------------
        \*args
            The arguments to to use.
        \*\*kwargs
            The keyword arguments to use.
        """

        def restart_when_over(fut, *, args=args, kwargs=kwargs):
            self._task.remove_done_callback(restart_when_over)
            self.start(*args, **kwargs)

        if self._can_be_cancelled():
            self._task.add_done_callback(restart_when_over)
            self._task.cancel()

    def add_exception_type(self, exc):
        r"""Adds an exception type to be handled during the reconnect logic.

        This function is useful if you're interacting with a 3rd party library that
        raises its own set of exceptions.

        Parameters
        ------------
        exc: Type[:class:`BaseException`]
            The exception class to handle.

        Raises
        --------
        TypeError
            The exception passed is either not a class or not inherited from :class:`BaseException`.
        """
        if not inspect.isclass(exc):
            raise TypeError('{0!r} must be a class.'.format(exc))
        if not issubclass(exc, BaseException):
            raise TypeError('{0!r} must inherit from BaseException.'.format(exc))

        self._valid_exception = (*self._valid_exception, exc)

    def clear_exception_types(self):
        """Removes all exception types that are handled.

        .. note::

            This operation obviously cannot be undone!
        """
        self._valid_exception = tuple()

    def remove_exception_type(self, exc):
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
        self._valid_exception = tuple(x for x in self._valid_exception if x is not exc)
        return len(self._valid_exception) != old_length

    def get_task(self):
        """Optional[:class:`asyncio.Task`]: Fetches the internal task or ``None`` if there isn't one running."""
        return self._task

    def is_being_cancelled(self):
        """Whether the task is being cancelled."""
        return self._is_being_cancelled

    def failed(self):
        """:class:`bool`: Whether the internal task has failed.

        .. versionadded:: 1.2.0
        """
        return self._has_failed

    def before_loop(self, coro):
        """A decorator that registers a coroutine to be called before the loop starts running.

        The coroutine must take no arguments (except ``self`` in a class context).

        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register before the loop runs.

        Raises
        -------
        TypeError
            The function was not a coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError('Expected coroutine function, received {0.__name__!r}.'.format(type(coro)))

        self._before_loop = coro
        return coro

    def after_loop(self, coro):
        """A decorator that register a coroutine to be called after the loop finished running.

        The coroutine must take no arguments (except ``self`` in a class context).

        .. note::

            This coroutine is called even during cancellation. If it is desirable
            to tell apart whether something was cancelled or not, check to see
            whether :meth:`is_being_cancelled` is ``True`` or not.

        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register after the loop finishes.

        Raises
        -------
        TypeError
            The function was not a coroutine.
        """

        if not inspect.iscoroutinefunction(coro):
            raise TypeError('Expected coroutine function, received {0.__name__!r}.'.format(type(coro)))

        self._after_loop = coro
        return coro

    def change_interval(self, *, seconds=0, minutes=0, hours=0):
        """Changes the interval for the sleep time.

        .. note::

            This only applies on the next loop iteration. If it is desirable for the change of interval
            to be applied right away, cancel the task with :meth:`cancel`.

        .. versionadded:: 1.2.0

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
        ValueError
            An invalid value was given.
        """

        sleep = seconds + (minutes * 60.0) + (hours * 3600.0)
        if sleep >= MAX_ASYNCIO_SECONDS:
            fmt = 'Total number of seconds exceeds asyncio imposed limit of {0} seconds.'
            raise ValueError(fmt.format(MAX_ASYNCIO_SECONDS))

        if sleep < 0:
            raise ValueError('Total number of seconds cannot be less than zero.')

        self._sleep = sleep
        self.seconds = seconds
        self.hours = hours
        self.minutes = minutes

def loop(*, seconds=0, minutes=0, hours=0, count=None, reconnect=True, loop=None):
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
    ---------
    :class:`Loop`
        The loop helper that handles the background task.
    """
    def decorator(func):
        return Loop(
            func, seconds=seconds, minutes=minutes, hours=hours,
            count=count, reconnect=reconnect, loop=loop)

    return decorator
