from __future__ import annotations

from typing import AsyncIterator, TypeVar

from async_extensions.collecting import collect_iterable_results
from iters.async_utils import async_iter, async_list
from typing_aliases import AnyErrorType, AnyIterable, is_instance
from wraps.primitives.result import is_error

__all__ = ("flatten_ignoring",)

T = TypeVar("T")


async def flatten_ignoring(
    iterables: AnyIterable[AnyIterable[T]], *ignore: AnyErrorType
) -> AsyncIterator[T]:
    coroutines = [async_list(iterable) async for iterable in async_iter(iterables)]

    results = await collect_iterable_results(coroutines)

    for result in results:
        if is_error(result):
            error = result.unwrap_error()

            if is_instance(error, ignore):
                continue

            raise error

        else:
            for item in result.unwrap():
                yield item
