.. _setup_logging

Setting Up Logging
==================

gd.py uses :mod:`logging` module to log different information.

By default, it is required to setup the logging by hand,
however, gd.py provides a simple way to set up logging
messages into the console::
    import gd
    gd.setup_basic_logging()

As it can be seen, everything basic is quite simple.
