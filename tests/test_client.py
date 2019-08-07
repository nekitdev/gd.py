import gd

client = gd.Client()

async def test_coro():
    rob = await client.get_user(71)
    print('get_user() ->', rob)
    abstract = await client.search_user('RobTop')
    rob = await abstract.to_user()
    print('search_user() ->', abstract, 'to_user() ->', rob)
    level = await client.get_level(44622744)
    print('get_level() ->', level)
    # ...

gd.utils.run(test_coro())
