.. currentmodule:: gd

Levels
======

Main atoms of Geometry Dash are levels; gd.py allows searching, interacting with, modifying and uploading them.

Here is an example of commenting a level::

    client = gd.Client()

    await client.login('username', 'password')

    level = await client.get_level(30029017)

    await level.comment('gd.py test comment')

Level
-----

.. autoclass:: Level
    :inherited-members:
    :members:

Difficulty
----------

.. autofunction:: get_actual_difficulty

Password
--------

.. autoclass:: Password
    :members:

Searching
---------

gd.py also provides a convenient way of searching for different levels::

    client = gd.Client()

    async for level in client.search_levels("Bloodlust"):
        print(level.name)

    # also by filters!

    async for level in client.search_levels(filters=gd.Filters.with_song(1, custom=False)):
        print(level.rating)

Filters
-------

.. autoclass:: Filters
    :members:

Geometry Dash has different level packs to play; currently, there are two of those:
Map Packs and Gauntlets.

Here is an example of fetching levels of a Fire gauntlet::

    client = gd.Client()

    fire_gauntlet = await client.get_gauntlets().get(name="Fire Gauntlet")

    for level in await fire_gauntlet.get_levels():
        print(level.id, level.rating, level.name)

Level Packs
-----------

.. autoclass:: MapPack
    :inherited-members:
    :members:

.. autoclass:: Gauntlet
    :inherited-members:
    :members:
