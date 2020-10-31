.. currentmodule:: gd.api

Save API
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

.. autoclass:: LevelStore
    :members:

.. autoclass:: LevelValues
    :members:

Level Collection
----------------

.. autoclass:: LevelCollection
    :members:

LevelAPI
--------

.. autoclass:: LevelAPI
    :inherited-members:
    :members:
