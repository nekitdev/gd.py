import pytest

from gd.client import Client

client = Client()


@pytest.mark.asyncio
async def test_ping() -> None:
    await client.ping()
