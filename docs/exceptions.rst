.. currentmodule:: gd

Exceptions
==========

gd.py has stable exception system, which leads better understanding of errors.
Below is a list of current existing exceptions.

Exception List
--------------

.. autoexception:: GDException

.. autoexception:: ClientException

.. autoexception:: EditorError

.. autoexception:: HTTPError

.. autoexception:: MissingAccess

.. autoexception:: SongRestrictedForUsage

.. autoexception:: LoginFailure
    :members:

.. autoexception:: NothingFound

.. autoexception:: NotLoggedError

Exception Hierarchy
-------------------

.. code-block:: python3

    GDException (Exception)
        EditorError
        ClientException
            HTTPError
            MissingAccess
            SongRestrictedForUsage
            LoginFailure
            NothingFound
            NotLoggedError
