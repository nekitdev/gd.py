gd.py
=====

.. image:: https://img.shields.io/pypi/l/gd.py.svg
    :target: https://opensource.org/licenses/MIT
    :alt: Project License

.. image:: https://travis-ci.com/NeKitDS/gd.py.svg?branch=master
    :target: https://travis-ci.com/NeKitDS/gd.py
    :alt: Build Status

.. image:: https://img.shields.io/pypi/v/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: PyPI Library Version

.. image:: https://img.shields.io/pypi/pyversions/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Required Python Versions

.. image:: https://img.shields.io/pypi/status/gd.py.svg
    :target: https://github.com/NeKitDS/gd.py/blob/master/gd
    :alt: Project Development Status

.. image:: https://img.shields.io/pypi/dw/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Library Downloads/Week

.. image:: https://readthedocs.org/projects/gdpy/badge/?version=latest
    :target: https://gdpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://api.codacy.com/project/badge/Grade/4bd8cfe7a66e4250bc23b21c4e0626b6
    :target: https://app.codacy.com/project/NeKitDS/gd.py/dashboard
    :alt: Code Quality [Codacy]

.. image:: https://img.shields.io/coveralls/github/NeKitDS/gd.py
    :target: https://coveralls.io/github/NeKitDS/gd.py
    :alt: Code Coverage

.. image:: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.herokuapp.com%2Fnekit%2Fpledges
    :target: https://patreon.com/nekit
    :alt: Patreon Page [Support]

gd.py is a library that provides its users ability to interact with servers of Geometry Dash.

Key Features
------------

- Modern Pythonic API
- High coverage of the supported Geometry Dash API
- Using ``async`` and ``await`` syntax

Installing
----------

**Python 3.5.3 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py

    # Windows
    py -3 -m pip install -U gd.py

You can also install optional **aioconsole** package,
which can be used to run async functions in repl:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py[console]

    # Windows
    py -3 -m pip install -U gd.py[console]

To install the developer version, run these commands:

.. code:: sh

    $ git clone https://github.com/NeKitDS/gd.py
    $ cd gd.py
    $ python3 -m pip install -U .[dev]

Quick example
-------------

Please note: gd.py writes the new method for coroutines, called 'run'.

.. code:: python

    import gd

    client = gd.Client()
    
    async def test():
        song = await client.get_song(633206)
        print(song.name)

    client.run(test())

    # OUTPUT: Random Song 01

You can find more examples in examples directory.

NOTICE
------

Developers of this library do not own any images in `resources <https://github.com/NeKitDS/gd.py/blob/master/gd/graphics/resources>`_ package. All of them were created and are owned by the Developer of Geometry Dash - Robert Topala (aka `RobTop <http://robtopgames.com/>`_).

Credits
-------

Thanks to `Alex1304 <https://github.com/Alex1304>`_ for inspiring the creation of this library.

Credits to `Rapptz <https://github.com/Rapptz>`_ and `discord.py <https://github.com/Rapptz/discord.py>`_ library developers; `tasks <https://github.com/Rapptz/discord.py/blob/master/discord/ext/tasks>`_ package in discord.py is a base for `tasks.py <https://github.com/NeKitDS/gd.py/blob/master/gd/utils/tasks.py>`_ file.

Authors
-------

This project is mainly developed by `NeKitDS <https://github.com/NeKitDS>`_,
with help of `blue <https://github.com/d3vblue>`_. Big thanks to `cos8o <https://github.com/cos8o>`_ and `SMJS <https://github.com/SMJSGaming>`_ for helping
to make several requests. Also thanks to `cos8o <https://github.com/cos8o>`_ again for developing `GDCrypto <https://github.com/cos8o/GDCrypto>`_ library,
which was used as a base for `crypto <https://github.com/NeKitDS/gd.py/blob/master/gd/utils/crypto>`_ package.

Links
-----

- `Documentation <https://gdpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/9xhdQFR>`_
- `Geometry Dash Discord Server <https://discord.gg/xkgrP29>`_
