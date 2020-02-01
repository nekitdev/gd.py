.. currentmodule:: gd

API Reference
=============

The following section outlines the API of gd.py.

.. note::

    See :ref:`sync` for better understanding about ways to run coroutines synchronously.

    You can find gd.py Developers API here: :ref:`development_api`.

Version Related Info
--------------------

There are two main ways to get version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.1.2rc1'``. This is based
    off of :pep:`440`.

Logging
-------

.. note::

    This module uses the Python logging module to log debug and error messages
    in an output independent way. If the logging is not configured,
    these logs will not be output anywhere. See :ref:`setup_logging` for 
    more information on how to set up the logging module with gd.py.

.. autofunction:: setup_logging

Client
------

.. warning::

    If you ever need to initialize any object by hand, please follow this:

    .. code-block:: python3

        level = gd.Level(id=30029017)

    Now let us do something, supposing that you have logged in client.

    .. code-block:: python3

        await level.comment('Here is some comment.')  # ERROR!

    The point is, there is no client attached to this level.
    You can attach a client to an instance of AbstractEntity like that:

    .. code-block:: python3

        level.attach_client(client)
        # or
        level = gd.Level(id=30029017, client=client)

    Do not forget this when writing your programs.

.. autoclass:: Client
    :members:

Filters
-------
.. autoclass:: Filters
    :members:

Paginator
---------

.. autofunction:: paginate

.. autoclass:: Paginator
    :members:

AbstractEntity
--------------

.. autoclass:: AbstractEntity
    :members:

Level
-----

.. autoclass:: Level
    :members:

Level Packs
-----------

.. autoclass:: MapPack
    :members:

.. autoclass:: Gauntlet
    :members:

Song
----

.. autoclass:: Song
    :members:

User
----

.. autoclass:: AbstractUser
    :members:

.. autoclass:: LevelRecord
    :members:

.. autoclass:: UserStats
    :members:

.. autoclass:: User
    :members:

Icon Set and Color
------------------

.. autoclass:: IconSet
    :members:

.. autoclass:: Color
    :members:

Comment
-------

.. autoclass:: Comment
    :members:

Friend Request
--------------

.. autoclass:: FriendRequest
    :members:

Message
-------

.. autoclass:: Message
    :members:

.. currentmodule:: gd.api

Game API
--------

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

.. autoclass:: Editor
    :members:

.. autoclass:: Object
    :members:

.. autoclass:: HSV
    :members:

.. autoclass:: ColorChannel
    :members:

.. currentmodule:: gd

Enums
-----

.. autoclass:: NEnum
    :members:

    .. automethod:: NEnum.from_value

.. note:: The following classes are derived from :class:`NEnum`.

.. autoclass:: MessagePolicyType

.. autoclass:: CommentPolicyType

.. autoclass:: FriendRequestPolicyType

.. autoclass:: StatusLevel

.. autoclass:: IconType

.. autoclass:: LevelLength

.. autoclass:: LevelDifficulty

.. autoclass:: DemonDifficulty

.. autoclass:: TimelyType

.. autoclass:: CommentType

.. autoclass:: MessageOrRequestType

.. autoclass:: CommentStrategy

.. autoclass:: LevelLeaderboardStrategy

.. autoclass:: SearchStrategy

.. autoclass:: ServerError

Exceptions
----------

.. autoexception:: GDException

.. autoexception:: ClientException

.. autoexception:: PaginatorException

.. autoexception:: FailedConversion
    :members:

.. autoexception:: EditorError

.. autoexception:: HTTPNotConnected

.. autoexception:: MissingAccess

.. autoexception:: SongRestrictedForUsage

.. autoexception:: LoginFailure
    :members:

.. autoexception:: FailedToChange

.. autoexception:: NothingFound

.. autoexception:: NotLoggedError

.. autoexception:: PagesOutOfRange

Exception Hierarchy
-------------------

.. code-block:: python3

    GDException (Exception)
        EditorError
        FailedConversion
        ClientException
            HTTPNotConnected
            MissingAccess
            SongRestrictedForUsage
            LoginFailure
            FailedToChange
            NothingFound
            NotLoggedError
        PaginatorException
            PagesOutOfRange

.. currentmodule:: gd.utils

Useful Utils
------------

.. autofunction:: run_blocking_io

.. autofunction:: run

.. autofunction:: acquire_loop

.. autofunction:: cancel_all_tasks

.. autofunction:: wait

.. autofunction:: find

.. autofunction:: get

.. autofunction:: unique

.. autofunction:: value_to_enum
