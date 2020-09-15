.. currentmodule:: gd

Setting Up Logging
==================

gd.py uses :mod:`logging` module to log different information.

By default, it is required to setup the logging by hand,
however, gd.py provides a simple way to set up logging all
messages into the console::

    import gd
    gd.setup_logging()

.. autofunction:: setup_logging

If something more specific is required, things can still be simple.

Let's suppose it is required to write all the warnings/errors and critical
messages into a file, for instance, ``geometry_dash.log``::

    import logging
    import gd

    FORMAT = "[{levelname}] ({name}): {message}"

    gd.setup_logging(
        level=logging.WARNING,  # only warnings/errors/critical will be displayed
        format_string=FORMAT,  # [LEVEL] (gd.some_module): Some message here.
        filename="geometry_dash.log",  # file to log into
    )

See :mod:`logging` documentation for more information about handling loggers.
