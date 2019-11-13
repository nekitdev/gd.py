.. _sync:

.. currentmodule:: gd.utils

Synchronization Of Coroutines
=============================

gd.py introduces several methods to run coroutines synchronously.

Let's say we have this code:

.. code-block:: python3

    import gd

    async def test():
        return 13

    client = gd.Client()

Now, here are the methods:

1. client.run
-------------

.. code-block:: python3

    client.run(test()) -> 13

This method executes a coroutine in client's event loop.
This is equivalent to ``gd.utils.run(test(), loop=client.loop)``.

2. gd.utils.run
---------------

.. code-block:: python3

    gd.utils.run(test()) -> 13

This method sets event loop to None after execution;
that means, calling :func:`asyncio.get_event_loop`
will raise the RuntimeError.

3. coroutine.run
--------------------------

.. code-block:: python3

    test().run() -> 13

This method is created by gd.py.
Every time it is called, a new event loop is created,
and a coroutine is being run in it.
This method does not change event loop in a thread, though.

You can enable it by doing:

.. code-block:: python3

    import gd
    gd.synchronize()

Theoretically, it is possible to disable this method by doing ``gd.synchronize(False)``.
However, when creating a coroutine between activating those functions, the behaviour becomes hard to predict.
That is why gd.py developers recommend to either have this method either turned on or off.
