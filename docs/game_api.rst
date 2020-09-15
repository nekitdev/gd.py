.. currentmodule:: gd.api

Game API
========

gd.py implements an interface to interact with saves of Geometry Dash.

Save
----

.. warning::

    **It is recommended to do a backup before working with saves.**

Main save/load functionality is contained in :class:`~gd.api.SaveUtils`,
exported and intended to be used as ``gd.api.save`` instance.

Example of loading a local database::

    import gd
    database = gd.api.save.load()

That simple? Yeah, that's *python*! Everything is simple.

.. autoclass:: SaveUtils
    :members:

Database
--------

Database is *python* interface to saves of Geometry Dash.

Example of working with it::

    db = gd.api.create_db()

    print(db.load_my_levels())
    # LevelCollection[<LevelAPI id=... version=... name=...>, ...]

    levels = db.levels
    # <Part len=...>

    print(levels.get("LLM_02", 0))
    # {"LLM_01": {...}, "LLM_02": ..., ...}

.. autoclass:: Part
    :members:

.. autoclass:: Database
    :members:

Level Editing
-------------

gd.py provides convenient API for creating and editing levels.

You can create objects like this::

    from gd.api import Object

    obj = Object(id=1, x=150, y=150).add_groups(1)
    # <Object id=1 x=150 y=150 groups={1}>

    string = obj.dump()
    # "1,1,2,150,3,150,57,1"

And open editor, like the following::

    from gd.api import Editor

    # assume we have our "obj" from above

    editor = Editor()

    editor.add_objects(obj)

    string = editor.dump()
    # "...;1,1,2,150,3,150,57,1;"

There is an option to load the level's editor::

    import gd

    client = gd.Client()

    level = client.run(client.get_level(30029017))

    editor = level.open_editor()

gd.py also gives some helpers in case user does not know some values::

    from gd.api import Object

    obj = Object(x=150, y=150, lock_to_player_x=True, target_group_id=1)
    # <Object id=1 x=150 y=150 target_group_id=1 lock_to_player_x=True>

    obj.set_id("trigger:move")  # move trigger
    # <Object id=901 x=150 y=150 target_group_id=1 lock_to_player_x=True>

    obj.set_easing("sine_in_out")
    # <Object id=901 x=150 y=150 easing=Easing.SINE_IN_OUT target_group_id=1 lock_to_player_x=True>

.. autofunction:: get_id

Editor
------

.. autoclass:: Editor
    :members:

Guidelines
----------

.. autoclass:: Guidelines
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

ColorCollection
---------------

.. autoclass:: ColorCollection
    :members:

Object
------

.. autoclass:: Object
    :members:
