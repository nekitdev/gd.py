.. currentmodule:: gd

API Reference
=============

The following section outlines the API of gd.py.

.. note::

    This module uses the Python logging module to log debug and error messages
    in an output independent way. If the logging is not configured,
    these logs will not be output anywhere. See :ref:`setup_logging` for 
    more information on how to set up the logging module with gd.py.

.. note::

    See :ref:`development_api` for gd.py Developers API.

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

Client
------

.. autoclass:: Client
    :members:

Filters
-------
.. autoclass:: Filters
    :members

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

- :exc:`GDException` (:exc:`Exception`)
    - :exc:`FailedConversion`
    - :exc:`ClientException`
        - :exc:`HTTPNotConnected`
        - :exc:`FailedCaptcha`
        - :exc:`MissingAccess`
        - :exc:`SongRestrictedForUsage`
        - :exc:`LoginFailure`
        - :exc:`FailedToChange`
        - :exc:`NothingFound`
        - :exc:`NotLoggedError`
    - :exc:`PaginatorException`
        - :exc:`PagesOutOfRange`

.. currentmodule:: gd.utils

Useful Utils
------------

.. autofunction:: run

.. autofunction:: cancel_all_tasks

.. autofunction:: wait

.. autofunction:: find

.. autofunction:: get

.. autofunction:: value_to_enum

.. autofunction:: convert_to_type
