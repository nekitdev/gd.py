import pytest

import gd

client = gd.Client()


@pytest.mark.asyncio
async def test_ping() -> None:
    ping = await client.ping_server()

    assert ping
