.. currentmodule:: gd

Version Related Info
====================

There are two main ways to get version information about the library.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.1.2rc1'``. This is based
    off of :pep:`440`.
