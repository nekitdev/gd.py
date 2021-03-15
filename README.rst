gd.py
=====

.. image:: https://img.shields.io/pypi/l/gd.py.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://travis-ci.com/nekitdev/gd.py.svg?branch=master
    :target: https://travis-ci.com/nekitdev/gd.py
    :alt: Build Status

.. image:: https://img.shields.io/pypi/v/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: PyPI Library Version

.. image:: https://img.shields.io/pypi/pyversions/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Required Python Versions

.. image:: https://img.shields.io/pypi/status/gd.py.svg
    :target: https://github.com/nekitdev/gd.py/tree/master/gd
    :alt: Project Development Status

.. image:: https://img.shields.io/pypi/dw/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Library Downloads/Week

.. image:: https://readthedocs.org/projects/gdpy/badge/?version=latest
    :target: https://gdpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://api.codacy.com/project/badge/Grade/4bd8cfe7a66e4250bc23b21c4e0626b6
    :target: https://app.codacy.com/project/nekitdev/gd.py/dashboard
    :alt: Code Quality [Codacy]

.. image:: https://img.shields.io/coveralls/github/nekitdev/gd.py
    :target: https://coveralls.io/github/nekitdev/gd.py
    :alt: Code Coverage

gd.py is a library that provides its users ability to interact with servers, client and memory of Geometry Dash.

Key Features
------------

- Modern Pythonic API
- High coverage of the supported Geometry Dash API
- Using ``async`` and ``await`` syntax

Installing
----------

**Python 3.6 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py

    # Windows
    py -3 -m pip install -U gd.py

Additional Dependencies
-----------------------

There are many dependencies that either extend functionality of the library or are used in its development.

- ``crypto`` is required to decrypt saves on MacOS;
- ``console`` is needed to run IPython console;
- ``docs`` are used to build docs;
- ``image`` installs PIL/Pillow for icon generating;
- ``lint`` adds formatters and linters to check improve code style;
- ``server`` is used for creating REST API around the library;
- ``speedups`` provides packages to speed the library up;
- ``test`` is required to run tests and check coverage.

You can install some extras like this:

.. code:: sh

    python -m pip install gd.py[image,speedups]

Install recommended ones:

.. code:: sh

    python -m pip install gd.py[prelude]

Or install all of them:

.. code:: sh

    python -m pip install gd.py[all]

Development Version
-------------------

You can install latest development version from GitHub:

.. code:: sh

    $ git clone https://github.com/nekitdev/gd.py.git
    $ cd gd.py
    $ python3 -m pip install -U .[all]

Quick example
-------------

Below is an example of fetching a song by its ID.

.. code:: python

    import gd

    client = gd.Client()
    
    async def test():
        song = await client.get_song(633206)
        print(song.name)

    client.run(test())

    # OUTPUT: Random Song 01

You can find more examples in examples directory.

Server
------

gd.py provides server with wrapper around itself, which can be started via a command:

.. code:: sh

    $ python3 -m gd server

Credits
-------

Thanks to `Alex1304 <https://github.com/Alex1304>`_ for inspiring the creation of this library.

Credits to `Rapptz <https://github.com/Rapptz>`_ and `discord.py <https://github.com/Rapptz/discord.py>`_ library developers; `tasks <https://github.com/Rapptz/discord.py/blob/master/discord/ext/tasks>`_ package in discord.py is a base for `gd.tasks <https://github.com/nekitdev/gd.py/blob/master/gd/tasks.py>`_ module.

Authors
-------

This project is mainly developed by `nekitdev <https://github.com/nekitdev>`_.
Big thanks to `cos8o <https://github.com/cos8o>`_ and `SMJS <https://github.com/SMJSGaming>`_ for helping
to make several requests. Also thanks to `cos8o <https://github.com/cos8o>`_ again for developing `GDCrypto <https://github.com/cos8o/GDCrypto>`_ library,
which was used as a base for `gd.crypto <https://github.com/nekitdev/gd.py/blob/master/gd/crypto.py>`_ module.

Links
-----

- `Documentation <https://gdpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/KtJkbut>`_
- `Geometry Dash Discord Server <https://discord.gg/xkgrP29>`_
