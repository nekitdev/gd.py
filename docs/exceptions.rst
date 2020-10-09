.. currentmodule:: gd

Exceptions
==========

gd.py has stable exception system, which leads better understanding of errors.
Below is a list of current existing exceptions.

Exception List
--------------

.. autoclass:: GDException
    :inherited-members:
    :members:

.. autoclass:: HTTPException
    :inherited-members:
    :members:

.. autoclass:: HTTPError
    :inherited-members:
    :members:

.. autoclass:: HTTPStatusError
    :inherited-members:
    :members:

.. autoclass:: ClientException
    :inherited-members:
    :members:

.. autoclass:: MissingAccess
    :inherited-members:
    :members:

.. autoclass:: SongRestricted
    :inherited-members:
    :members:

.. autoclass:: LoginFailure
    :inherited-members:
    :members:

.. autoclass:: NothingFound
    :inherited-members:
    :members:

.. autoclass:: NotLoggedError
    :inherited-members:
    :members:

.. autoclass:: DataException
    :inherited-members:
    :members:

.. autoclass:: DeError
    :inherited-members:
    :members:

.. autoclass:: SerError
    :inherited-members:
    :members:

.. autoclass:: XMLError
    :inherited-members:
    :members:

.. autoclass:: EditorError
    :inherited-members:
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
