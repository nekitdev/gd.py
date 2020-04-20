.. currentmodule:: gd.api

Game API
========

gd.py provides convenient API for creating and editing levels.

You can create objects like this:

.. code-block:: python3

    from gd.api import Object

    obj = Object(id=1, x=150, y=150, groups={1})
    # <gd.Object id=1 x=150 y=150 groups={1}>

    string = obj.dump()
    # '1,1,2,150,3,150,57,1'

And open editor, like the following:

.. code-block:: python3

    from gd.api import Editor

    # assume we have our 'obj' from above

    editor = Editor()

    editor.add_objects(obj)

    string = editor.dump()
    # '<some_data>;1,1,2,150,3,150,57,1;'

There is an option to load the level's editor:

.. code-block:: python3

    import gd

    client = gd.Client()

    level = client.run(client.get_level(30029017))

    editor = level.open_editor()

gd.py also gives some helpers in case user does not know some values:

.. code-block:: python3

    from gd.api import Object

    o = Object(x=150, y=150, lock_to_player_x=True, target_group_id=1)
    # <gd.Object id=1 x=150 y=150 target_group_id=1 lock_to_player_x=True>

    o.set_id('trigger:move')  # move trigger
    # <gd.Object id=901 x=150 y=150 target_group_id=1 lock_to_player_x=True>

    o.set_easing('sine_in_out')
    # <gd.Object id=901 x=150 y=150 easing=<gd.Easing.SineInOut: 13 (SineInOut)> target_group_id=1 lock_to_player_x=True>

.. autofunction:: get_id

Editor
------

.. autoclass:: Editor
    :members:

Header
------

.. autoclass:: Header
    :members:

LevelAPI
--------

.. autoclass:: LevelAPI
    :members:

HSV
---

.. autoclass:: HSV
    :members:

ColorChannel
------------

.. autoclass:: ColorChannel
    :members:

Object
------

.. autoclass:: Object
    :members:
