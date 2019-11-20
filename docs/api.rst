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

        # Now let us do something, supposing that you have logged in client.
        await level.comment('Here is some comment.')  # ERROR!

        # the point is, there is no client attached to this level.

        # you can attach a client to an instance of AbstractEntity like that:
        level.attach_client(client)
        # or like that:
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

.. autoclass:: UnregisteredUser
    :members:

.. autoclass:: AbstractUser
    :members:

.. autoclass:: LevelRecord
    :members:

.. autoclass:: UserStats
    :members:

.. autoclass:: User
    :members:

Icon Set and Colour
-------------------

.. autoclass:: IconSet
    :members:

.. autoclass:: Colour
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

Exceptions
----------

.. autoexception:: GDException

.. autoexception:: ClientException

.. autoexception:: PaginatorException

.. autoexception:: FailedConversion
    :members:

.. autoexception:: HTTPNotConnected

.. autoexception:: FailedCaptcha

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
        FailedConversion
        ClientException
            HTTPNotConnected
            FailedCaptcha
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

.. autofunction:: value_to_enum

.. autofunction:: convert_to_type
