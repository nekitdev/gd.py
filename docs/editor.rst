.. currentmodule:: gd.api

Level Editing
=============

gd.py provides convenient API for creating and editing levels.

You can create objects like this::

    from gd.api import Object

    obj = Object(id=1, x=150, y=150).add_groups(1)
    # <Object id=1 x=150 y=150 groups={1}>

    string = some_object.dump()
    # "1,1,2,150,3,150,57,1"

And open editor, like the following::

    from gd.api import Editor

    # assume we have our "some_object" from above

    editor = Editor()

    editor.add_objects(some_object)

    string = editor.dump()
    # "...;1,1,2,150,3,150,57,1;"

There is an option to load the level's editor::

    import gd

    client = gd.Client()

    level = client.run(client.get_level(30029017))

    editor = level.open_editor()

gd.py also gives some helpers in case user does not know some values::

    from gd.api import Object

    some_object = Object(x=150, y=150, lock_to_player_x=True, target_group_id=1)
    # <Object id=1 x=150 y=150 target_group_id=1 lock_to_player_x=True>

    some_object.set_id("trigger:move")  # move trigger
    # <Object id=901 x=150 y=150 target_group_id=1 lock_to_player_x=True>

    some_object.set_easing("sine_in_out")
    # <Object id=901 x=150 y=150 easing=Easing.SINE_IN_OUT target_group_id=1 lock_to_player_x=True>

.. autofunction:: get_id

Editor
------

.. autoclass:: Editor
    :inherited-members:
    :members:

Header
------

.. autoclass:: Header
    :inherited-members:
    :members:

HSV
---

.. autoclass:: HSV
    :inherited-members:
    :members:

ColorChannel
------------

.. autoclass:: ColorChannel
    :inherited-members:
    :members:

ColorCollection
---------------

.. autoclass:: ColorCollection
    :members:

Object
------

.. autoclass:: Object
    :inherited-members:
    :members:
