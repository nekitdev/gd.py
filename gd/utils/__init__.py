import asyncio

from .search_utils import find, get
from .decorators import benchmark

# for more comfortable coding
run = asyncio.run
wait = asyncio.wait
