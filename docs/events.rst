.. currentmodule:: gd

Event Reference
===============

gd.py provides a system for handling events, such as new daily levels or weekly demons.

Example
-------

Here is a simple usage example::

    import gd

    client = gd.Client()

    @client.listen_for("daily")  # listen_for returns a decorator
    async def on_new_daily(level):
        print(f"New daily level was set: {level.name} (ID: {level.id}).")

    gd.events.start()

This code snippet will print a message every time a new level is getting daily.

Example Explanation
-------------------

``client.listen_for('event_type')`` creates a listener with the ``client``,
and schedules the loop task.

``gd.events.start()`` runs all the scheduled tasks in another thread.

.. warning::

    Do not call ``client.listen_for`` after  ``gd.events.start()`` was called,
    since it simply will not have any effect and will not start another listener.

Built-In Listeners
------------------

+----------------+--------------------------------------+----------------------------------------------+
|           name |                       event callback |                               listener class |
+================+======================================+==============================================+
| daily          | :meth:`~gd.Client.on_new_daily`      | :class:`~gd.events.TimelyLevelListener`      |
+----------------+--------------------------------------+----------------------------------------------+
| weekly         | :meth:`~gd.Client.on_new_weekly`     | :class:`~gd.events.TimelyLevelListener`      |
+----------------+--------------------------------------+----------------------------------------------+
| rate           | :meth:`~gd.Client.on_level_rated`    | :class:`~gd.events.RateLevelListener`        |
+----------------+--------------------------------------+----------------------------------------------+
| unrate         | :meth:`~gd.Client.on_level_unrated`  | :class:`~gd.events.RateLevelListener`        |
+----------------+--------------------------------------+----------------------------------------------+
| friend_request | :meth:`~gd.Client.on_friend_request` | :class:`~gd.events.MessageOrRequestListener` |
+----------------+--------------------------------------+----------------------------------------------+
| message        | :meth:`~gd.Client.on_message`        | :class:`~gd.events.MessageOrRequestListener` |
+----------------+--------------------------------------+----------------------------------------------+
| level_comment  | :meth:`~gd.Client.on_level_comment`  | :class:`~gd.events.LevelCommentListener`     |
+----------------+--------------------------------------+----------------------------------------------+

.. autoclass:: gd.events.TimelyLevelListener

.. autoclass:: gd.events.RateLevelListener

.. autoclass:: gd.events.MessageOrRequestListener

.. autoclass:: gd.events.LevelCommentListener

Running Manually
----------------

If you wish to run the listener normally (blocking the main thread), you can do the following:

.. code-block:: python3

    import gd

    loop = gd.utils.acquire_loop()

    client = gd.Client()
    client.listen_for('daily')

    @client.event
    async def on_new_daily(level):
        print(level.creator.name)

    gd.events.run(loop)

Instead of running this:

.. code-block:: python3

    gd.events.run(loop)

You can use this:

.. code-block:: python3

    gd.events.enable(loop)
    loop.run_forever()

This allows for using gd.py, for example, in the discord.py bot:

.. code-block:: python3

    from discord.ext import commands
    import gd

    bot = commands.Bot(command_prefix="!")
    client = gd.Client()
    bot.client = client  # attach the client in case you might need to use it

    @client.listen_for("daily")
    async def on_new_daily(level: gd.Level) -> None:
        ...  # you can do something with your bot here

    gd.events.enable(bot.loop)
    bot.run("BOT_TOKEN")

Event handlers with @client.event
---------------------------------

As shown in examples above, new implementation for an event can be registered
with ``@client.event`` decorator. See :meth:`~gd.Client.event` for more info.

Event handlers with subclassing gd.Client
-----------------------------------------

Another way to write an implementation for ``on_event`` task is to subclass :class:`~gd.Client`.

.. code-block:: python3

    import gd

    class MyClient(gd.Client):
        async def on_new_daily(self, level: gd.Level) -> None:
            print(level)

    client = MyClient()

    client.listen_for("daily")

    gd.events.start()

Functions
---------

.. currentmodule:: gd.events

.. autofunction:: enable

.. autofunction:: run

.. autofunction:: start

.. autofunction:: disable

.. autofunction:: attach_to_loop

Creating Custom Listeners
-------------------------

It is possible to implement your own listeners.

The main idea is subclassing ``AbstractListener`` and creating your own ``scan`` method in there.

.. autoclass:: AbstractListener
    :members:

.. code-block:: python3

    import gd

    class CustomListener(gd.events.AbstractListener):
        def __init__(self, client, delay=10.0):
            # you can add additional arguments here
            super().__init__(client=client, delay=delay)  # call listener init

        async def scan(self):
            # do something here
            ...
            # dispatch event
            dispatcher = self.client.dispatch("event", *args, **kwargs)
            # dispatches on_<event> with args and kwargs
            self.loop.create_task(dispatcher)  # schedule execution

    client.listener.append(CustomListener(client, 5.0))

    gd.events.start()
