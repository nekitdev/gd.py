from __future__ import annotations

from typing import AsyncIterator, Type, TypeVar

from async_extensions.collect import collect_iterable_results
from iters.async_utils import async_iter, async_list
from typing_aliases import AnyError, AnyIterable, is_instance
from wraps.result import is_error

__all__ = ("run_iterables",)

T = TypeVar("T")


async def run_iterables(
    iterables: AnyIterable[AnyIterable[T]], *ignore: Type[AnyError]
) -> AsyncIterator[T]:
    coroutines = [async_list(iterable) async for iterable in async_iter(iterables)]

    results = await collect_iterable_results(coroutines)

    for result in results:
        if is_error(result):
            error = result.unwrap_error()

            if is_instance(result, ignore):
                continue

            raise error

        else:
            for item in result.unwrap():
                yield item
