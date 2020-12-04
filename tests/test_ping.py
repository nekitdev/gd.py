import gd

client = gd.Client()


async def test_ping() -> None:
    ping = await client.ping_server()

    assert ping
