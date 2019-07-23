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

.. autoclass:: Client
    :members:
