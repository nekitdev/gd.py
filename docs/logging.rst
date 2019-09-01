.. _setup_logging:

Setting Up Logging
==================

gd.py uses :mod:`logging` module to log different information.

By default, it is required to setup the logging by hand,
however, gd.py provides a simple way to set up logging all
messages into the console::

    import gd
    gd.setup_basic_logging()

As it can be seen, nothing is too hard.

Although, here is a snippet of how this funcion works::

    import logging
    def setup_basic_logging(*, file=None):
        handler = (
            logging.StreamHandler() if file is None
            else logging.FileHandler(file)
        )
        handler.setFormatter(
            logging.Formatter('[%(levelname)s] (%(asctime)s) {%(name)s}: %(message)s')
        )
        log.setLevel(logging.DEBUG)
        log.addHandler(handler)

If something more specific is required, things can get a bit harder.

Let's suppose it is required to write all the warnings/errors and critical
messages into a file, for instance, ``geometry_dash.log``::

    import logging
    import gd
    log = gd.log  # choose log we need to set handler to
    # configure handler
    handler = logging.FileHandler('geometry_dash.log')  # for logging in files
    # set format of displaying
    handler.setFormatter(
        logging.Formatter('[%(levelname)s] (%(name)s): %(message)s')
    )  # now displayed as [LEVEL] (gd.some_module): Some message here.
    log.addHandler(handler)  # add created handler
    log.setLevel(logging.WARNING)  #  only warnings/errors/critical will be displayed

See :mod:`logging` documentation for more information about handling loggers.
