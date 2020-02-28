.. currentmodule:: gd.utils

Useful Utils
============

gd.py provides a plenty of useful and handy functions.

Async Helpers
-------------

Whether they are for async things::

    import asyncio

    def file_io():
        with open('some_file.log', 'w') as file:
            file.write('test')

    await gd.utils.run_blocking_io(file_io)

    await gd.utils.gather(
        asyncio.sleep(1),
        asyncio.sleep(2),
        asyncio.sleep(3)
    )  # will sleep for 3 seconds only

.. autofunction:: run_blocking_io

.. autofunction:: run

.. autofunction:: acquire_loop

.. autofunction:: cancel_all_tasks

.. autofunction:: wait

.. autofunction:: gather

Sequence Helpers
----------------

Or for sequences::

    client = gd.Client()

    level = await client.get_level(30029017)

    comments = await level.get_comments(amount=1000)

    over_100_likes = gd.utils.find(lambda comment: comment.rating > 100, comments)
    # may be None, though

.. autofunction:: find

.. autofunction:: get

.. autofunction:: unique
