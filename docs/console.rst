Console Usage
=============

gd.py has some useful console commands.

.. note::
    ``python`` in commands corresponds to Python's executable file.
    gd.py *might* be installed in your path so you can run the following:

    .. code-block:: sh

        $ gd <command>

In case you need any help, you can do:

.. code-block:: sh

    $ python -m gd --help

    $ python -m gd -h

For example, there is a way to check gd.py dependencies and system version:

.. code-block:: sh

    $ python -m gd --version

    $ python -m gd -v

You can also get gd.py's documentation link (kinda useful, but eh):

.. code-block:: sh

    $ python -m gd --docs

    $ python -m gd -d

And, the most useful console feature of gd.py is its asynchronous console launcher:

.. code-block:: sh

    $ python -m gd --console

    $ python -m gd -c

.. warning:: Make sure you have ``aioconsole`` package installed. There are some ways to install it below.

    .. code-block:: sh

        $ python -m pip install -U aioconsole

        $ python -m pip install -U gd.py[console]
