.. currentmodule:: gd

Client
======

Client is the main entry point to interacting with Geometry Dash servers using gd.py.
It has many different methods which cover almost entire GD server API.

Typical usage is to create a client instance somewhere at the global scope,
and then run its methods in async functions::

    client = gd.Client()
    song = await client.get_song(1)
    # <gd.Song id=1 name='Chilled 1' author='Recoil'>

Client instances have ``session`` objects bind to them, which allow to run methods with custom arguments,
if needed. Every ``session`` object has ``http`` client object bound, that can be used for any request.

Here is more interesting client usage::

    client = gd.Client()

    level = await client.get_level(30029017)
    # <gd.Level id=30029017 name='VorteX' ...>

    # some counters
    total = 0
    count = 0

    # for each comment on the level, add its rating to total and increment count
    for comment in await level.get_comments(amount=1000000):  # all comments?
        count += 1
        total += comment.rating

    print('Average rating/comment on {0!r}: {1:.2f}.'.format(level.name, total/count))

Client objects also supported operations that require GD account.

Logging in account is fairly simple::

    client = gd.Client()
    await client.login('username', 'password')

Logged in Clients can like levels, post comments, send messages and friend requests, etc::

    client = gd.Client()
    # log in
    await client.login('username', 'password')

    rob = await client.find_user('RobTop')
    # <gd.AbstractUser name='RobTop' id=16 account_id=71>

    for level in await rob.get_levels():
        print(level.name, level.id)
        await level.like()  # hehe

    nekit = await client.fetch_user(5509312)
    # <gd.AbstractUser name='NeKitDS' id=17876467 account_id=5509312>

    # please do not spam me with those uwu ~ nekit
    await nekit.send_friend_request('Hey there from gd.py')

    bot = await client.search_user('GDBotAI')
    # <gd.User account_id=11676872 id=118270198 name='GDBotAI' ...>

    # send a message
    await bot.send('Ignore: gd.py', 'This is a message sent from gd.py')

Another example::

    client = gd.Client()
    # log in
    await client.login('username', 'password')

    for friend in await client.get_friends():
        print(friend.name)

You can even do this (I strongly do not recommend though)::

    level = await client.get_level(30029017)
    # <gd.Level id=30029017 name='VorteX' ...>

    await level.upload(id=0)  # reupload a level...

.. warning::

    If you ever need to initialize any object by hand, do not forget to attach a client:

    .. code-block:: python3

        level = gd.Level(id=30029017, client=client)

Client
------

.. autoclass:: Client
    :members:
