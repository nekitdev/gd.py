.. currentmodule:: gd.api

Game API
========

gd.py implements an interface to interact with saves of Geometry Dash.

Save
----

Main save/load functionality is contained in :class:`.SaveUtil`,
exported and intended to be used as ``gd.api.save`` instance.

Example of loading a local database:

.. code-block:: python3

    import gd
    database = gd.api.save.load()

That simple? Yeah, that's *python*! Everything is simple.

.. autoclass:: SaveUtil
    :members:

Database
--------

Database is *python* interface to saves of Geometry Dash.

.. code-block:: python3

    db = gd.api.make_db()

    print(db.load_my_levels())
    # LevelCollection[<gd.LevelAPI id=... version=... name=...>, ...]

    levels = db.levels
    # <gd.Part len=...>

    # {"LLM_01": {...}, "LLM_02": ..., ...}

    print(levels.get("LLM_02", 0))

.. autoclass:: Part
    :members:

.. autoclass:: Database
    :members:

Level Editing
-------------

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

Enums
-----

.. autoclass:: ObjectDataEnum
    :members:

.. autoclass:: ColorChannelProperties
    :members:

.. autoclass:: PlayerColor
    :members:

.. autoclass:: CustomParticleGrouping
    :members:

.. autoclass:: CustomParticleProperty1
    :members:

.. autoclass:: Easing
    :members:

.. autoclass:: PulseMode
    :members:

.. autoclass:: InstantCountComparison
    :members:

.. autoclass:: OrbType
    :members:

.. autoclass:: PadType
    :members:

.. autoclass:: PortalType
    :members:

.. autoclass:: PickupItemMode
    :members:

.. autoclass:: PulseType
    :members:

.. autoclass:: SpecialBlockType
    :members:

.. autoclass:: SpecialColorID
    :members:

.. autoclass:: TargetPosCoordinates
    :members:

.. autoclass:: TouchToggleMode
    :members:

.. autoclass:: TriggerType
    :members:

.. autoclass:: ZLayer
    :members:

.. autoclass:: MiscType
    :members:

.. autoclass:: Gamemode
    :members:

.. autoclass:: Speed
    :members:

.. autoclass:: SpeedConstant
    :members:

.. autoclass:: SpeedMagic
    :members:

.. autoclass:: GuidelinesColor
    :members:

.. autoclass:: LevelDataEnum
    :members:

.. autoclass:: LevelHeaderEnum
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

Object
------

.. autoclass:: Object
    :members:
