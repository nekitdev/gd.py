import pytest

from gd.async_iter import async_iterable
from gd.typing import AsyncIterator

pytestmark = pytest.mark.asyncio


async def test_async_iter() -> None:
    some_range = async_range(0, 10)

    n_0 = await some_range.next()

    assert isinstance(n_0, int)

    n_1 = await some_range.next()

    assert n_1 == 1

    n_list = await some_range.flatten()

    assert n_list == [2, 3, 4, 5, 6, 7, 8, 9]


@async_iterable
async def async_range(*range_args: int) -> AsyncIterator[int]:
    for number in range(*range_args):
        yield number
