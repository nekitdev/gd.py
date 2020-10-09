.. currentmodule:: gd

Users
=====

User system is one of the main parts of GD Server API.
gd.py provides convenient interface for simplifying interaction with them via modern pythonic code.

Here is a quick example of interacting with users::

    client = gd.Client()

    user = await client.get_user(71)
    # <User name='RobTop' id=16 account_id=71>

    async for comment in user.get_comment_history(pages=range(20)):
        print(comment.id, comment.rating, comment.body)

User
----

.. autoclass:: User
    :inherited-members:
    :members:

gd.py also provides interface to users' icons and colors::

    nekit = await client.get_user(5509312)
    # <User name='nekitdev' id=17876467 account_id=5509312>

    image = await nekit.generate_full(as_image=True)  # generate full icon set image

    image.save("nekit.png")

Color
-----

.. autoclass:: Color
    :members:
