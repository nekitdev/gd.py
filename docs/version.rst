.. currentmodule:: gd

Version Related Info
====================

There are two main ways to get version information about the library.

.. data:: __version__

    A string representation of the version. e.g. ``"1.0.0"``. This is based
    off of :pep:`440`.

.. data:: version_info

    Library version, wrapped into :class:`~gd.VersionInfo`, similar to :obj:`sys.version_info`.

    Just like :obj:`sys.version_info` the valid values for ``releaselevel`` are
    "alpha", "beta", "candidate" and "final".

.. data:: aiohttp_version

    Version of ``aiohttp``, wrapped into :class:`~gd.VersionInfo`.

.. data:: python_version

    Python version, wrapped into :class:`~gd.VersionInfo`.

.. autoclass:: VersionInfo
    :members:

.. autofunction:: make_version_info
