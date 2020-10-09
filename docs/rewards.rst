.. currentmodule:: gd

Rewards
=======

gd.py has interface that allows fetching chests and quests:

Example::

    client = gd.Client()

    await client.login("user", "password")  # must be logged in

    chests = await client.get_chests()
    # [<Chest id=... orbs=... diamonds=... shard_id=... shard_type=... keys=... count=... delta=h:m:s>, ...]

    quests = await client.get_quests()
    # [<Quest id=... name=... type=... amount=... reward=... delta=h:m:s>, ...]

Chest
-----

.. autoclass:: Chest
    :inherited-members:
    :members:

Quest
-----

.. autoclass:: Quest
    :inherited-members:
    :members:
