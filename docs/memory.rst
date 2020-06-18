.. currentmodule:: gd.memory

Memory Interaction
==================

.. warning::

    Please note that memory interaction is currently supported on Windows only.
    If you wish to contribute to adding MacOS memory interaction, feel free to open a pull request.

gd.py allows to interact with the memory of Geometry Dash.

Quick example of a program that will print a random message every time the player dies.

.. code-block:: python3

    import random  # for fun

    import gd

    messages = ["Get good.", "RIP", "F", "bruh", "hm..."]  # some messages to pick from

    # initialize memory object by acquiring process handle and base addresses
    memory = gd.memory.get_memory()
    do_print = True

    while True:
        if memory.is_dead():  # if player is dead
            if do_print:
                print(f"{random.choice(messages)} ({memory.get_percent()}%)")
            do_print = False
        else:
            do_print = True

Types
-----

There are several simple types gd.py support for reading/writing memory:
*Bool*, *Int32*, *Int64*, *Float*, *Double*, *String*.

They can be accessed like so:

.. code-block:: python3

    import gd

    print(gd.memory.Int32)
    # or
    print(gd.memory.Type.Double)

Enums
-----

.. autoclass:: Scene
    :members:

.. autoclass:: LevelType
    :members:

Buffer
------

.. autoclass:: Buffer
    :members:

Memory API
----------

.. autoclass:: MemoryType
    :members:

.. autoclass:: Memory
    :members:

.. autoclass:: WindowsMemory
    :members:

.. autoclass:: MacOSMemory
    :members:

.. autofunction:: get_memory
