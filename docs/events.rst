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

    @client.listen_for('daily')  # listen_for returns a client.event decorator
    async def on_new_daily(level):
        print('New daily level was set: {!r}.'.format(level))

    gd.events.start()

This code snippet will print a message every time a new level is getting daily.

Example Explanation
-------------------
``client.listen_for('event_type')`` creates a listener with the ``client``,
and schedules the loop task.

``gd.events.start()`` runs all the scheduled tasks in another thread.

Running Manually
----------------
If you wish to run the listener normally (blocking the main thread), you can do the following:

    .. code-block:: python3

        import gd

        loop = gd.utils.acquire_loop()
        gd.events.attach_to_loop(loop)

        client = gd.Client()
        client.listen_for('daily')

        @client.event
        async def on_new_daily(level):
            print(level.creator.name)

        gd.events.run(loop)  # or, simpler, loop.run_forever()

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

    client.listen_for('daily')

    gd.events.start()

Creating Custom Listeners
-------------------------

It is possible to implement your own listeners.

The main idea is subclassing ``AbstractListener`` and creating your own ``scan`` method in there.

.. code-block:: python3

    import gd

    class CustomListener(gd.events.AbstractListener):
        def __init__(self, client, delay=10.0, *, loop=None):
            # you can add additional arguments here
            super().__init__(client, delay, loop=loop)  # this line is required

        async def scan(self):
            # do something here
            ...
            # dispatch event
            dispatcher = self.client.dispatch('event', *args, **kwargs)
            # dispatches on_<event> with args and kwargs
            self.loop.create_task(dispatcher)  # schedule execution

    CustomListener(client, 5.0).enable()

    gd.events.start()
