.. currentmodule:: gd

API Reference
=============

The following section outlines the API of gd.py.

.. note::

    This module uses the Python logging module to log debug and error messages
    in an output independent way. If the logging is not configured,
    these logs will not be output anywhere. See :ref:`setup_logging` for 
    more information on how to set up the logging module with gd.py.

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

Paginator
---------

.. autoclass:: Paginator
    :members:

Level
-----

.. autoclass:: Level
    :members:

Song
----

.. autoclass:: Song
    :members:

AbstractUser
------------

.. autoclass:: AbstractUser
    :members:

User
----

.. autoclass:: User
    :members:

Icon Set
--------

.. autoclass:: IconSet
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

Exceptions
----------

.. autoexception:: GDException

.. autoexception:: ClientException

.. autoexception:: PaginatorException

.. autoexception:: MissingAccess

.. autoexception:: SongRestrictedForUsage

.. autoexception:: LoginFailure
    :members:

.. autoexception:: FailedToChange

.. autoexception:: NothingFound
    :members:

.. autoexception:: NotLoggedError

.. autoexception:: PagesOutOfRange

.. autoexception:: PaginatorIsEmpty

Exception Hierarchy
-------------------

- :exc:`Exception`
  - :exc:`GDException`
    - :exc:`ClientException`
      - :exc:`MissingAccess`
      - :exc:`SongRestrictedForUsage`
      - :exc:`LoginFailure`
      - :exc:`FailedToChange`
      - :exc:`NothingFound`
      - :exc:`NotLoggedError`
    - :exc:`PaginatorException`
      - :exc:`PagesOutOfRange`
      - :exc:`PaginatorIsEmpty`
