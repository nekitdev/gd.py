.. currentmodule:: gd

Exceptions
==========

gd.py has stable exception system, which leads better understanding of errors.
Below is a list of current existing exceptions.

Exception List
--------------

.. autoexception:: GDException

.. autoexception:: ClientException

.. autoexception:: PaginatorException

.. autoexception:: FailedConversion
    :members:

.. autoexception:: EditorError

.. autoexception:: HTTPError

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
            HTTPError
            MissingAccess
            SongRestrictedForUsage
            LoginFailure
            FailedToChange
            NothingFound
            NotLoggedError
        PaginatorException
            PagesOutOfRange
