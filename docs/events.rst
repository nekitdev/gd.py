.. _events:

.. currentmodule:: gd

Event Reference
===============

gd.py provides a system for handling events, such as new daily levels or weekly demons.

Example
-------
Here is a simple usage example:

.. code-block:: python3

    import gd

    client = gd.Client()

    @client.event
    async def on_new_daily(level):
        print('New daily level was set: {!r}.'.format(level))

    gd.events.add_client(client)
    gd.events.enable()
    gd.events.start()

This code snippet will print a message every time a new level is getting daily.

Example Explanation
-------------------
The last three lines of an example are important. Here is the explanation on what they are doing.

``gd.events.add_client(client)`` appends a ``client`` to a scanner, which calls the ``on_event`` method.

``gd.events.enable()`` schedules tasks in all default listeners.

And, finally, ``gd.events.start()`` runs all the scheduled tasks in another thread.

Running Manually
----------------
There is a way to run any of the default listeners manually:

.. code-block:: python3

    import gd

    daily_listener = gd.events.daily_listener

    client = gd.Client()

    daily_listener.add_client(client)

    @client.event
    async def on_new_daily(level):
        print('New daily was set!')

    daily_listener.enable()

    gd.events.start()

.. note:: It is recommended to start a scanner after defining event implementation.

If you wish to run the scanner normally (blocking the main thread), you can do the following:

    .. code-block:: python3

        import asyncio
        import gd

        client = gd.Client()

        @client.event
        async def on_new_daily(level):
            print(level.creator.name)

        loop = asyncio.get_event_loop()

        gd.events.attach_to_loop(loop)

        # tasks are now attached to the 'loop'

        gd.events.add_client(client)

        gd.events.enable()

        gd.events.run(loop)  # or, simplier, loop.run_forever()

There are two main ways to write an implementation for ``on_event`` task.

1. Using @client.event
----------------------
As shown in examples above, new implementation for an event can be registered
with ``@client.event`` decorator. See :meth:`.Client.event` for more info.

2. Subclassing gd.Client
------------------------
Another way to write an implementation for ``on_event`` task is to subclass :class:`.Client`.

.. code-block:: python3

    import gd

    class MyClient(gd.Client):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        async def on_new_daily(self, level):
            print(level)

    client = MyClient()

    gd.events.add_client(client)
    gd.events.enable()
    gd.events.run()

Important Note
--------------
If ``gd.events.start()`` was called, it is recommended to call ``gd.exit()`` to normally close the interpreter, or at least all scanners should be closed via ``gd.events.disable()``.
