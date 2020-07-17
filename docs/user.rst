.. currentmodule:: gd

Users
=====

User system is one of the main parts of GD Server API.
gd.py provides convenient interface for simplifying interaction with them via modern pythonic code.

Here is a quick example of interacting with users::

    client = gd.Client()

    user = await client.get_user(71)
    # <User account_id=71 id=16 name='RobTop' ...>

    for comment in await user.get_comment_history(pages=range(20)):
        print(comment.id, comment.rating, comment.body)

User
----

.. autoclass:: AbstractUser
    :members:

.. autoclass:: LevelRecord
    :members:

.. autoclass:: UserStats
    :members:

.. autoclass:: User
    :members:

gd.py also provides interface to users' icons and colors::

    nekit = await client.get_user(5509312)
    # <User account_id=5509312 id=17876467 name='NeKitDS' ...>

Icon Set and Color
------------------

.. autoclass:: IconSet
    :members:

.. autoclass:: Color
    :members:
