.. currentmodule:: gd

Exceptions
==========

gd.py has stable exception system, which leads better understanding of errors.
Below is a list of current existing exceptions.

Exception List
--------------

.. autoclass:: GDException
    :members:

.. autoclass:: HTTPException
    :members:

.. autoclass:: HTTPError
    :members:

.. autoclass:: HTTPStatusError
    :members:

.. autoclass:: ClientException
    :members:

.. autoclass:: MissingAccess
    :members:

.. autoclass:: SongRestricted
    :members:

.. autoclass:: LoginFailure
    :members:

.. autoclass:: NothingFound
    :members:

.. autoclass:: NotLoggedError
    :members:

.. autoclass:: DataException
    :members:

.. autoclass:: DeError
    :members:

.. autoclass:: SerError
    :members:

.. autoclass:: XMLError
    :members:

.. autoclass:: EditorError
    :members:

Exception Hierarchy
-------------------

- :class:`~gd.GDException` (:class:`Exception`)
    - :class:`~gd.HTTPException`
        - :class:`~gd.HTTPStatusError`
        - :class:`~gd.HTTPError`

    - :class:`~gd.ClientException`
        - :class:`~gd.MissingAccess`
        - :class:`~gd.SongRestricted`
        - :class:`~gd.LoginFailure`
        - :class:`~gd.NothingFound`
        - :class:`~gd.NotLoggedError`

    - :class:`~gd.DataException`
        - :class:`~gd.DeError`
        - :class:`~gd.SerError`
        - :class:`~gd.XMLError`
        - :class:`~gd.EditorErrror`
