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

**Python 3.6 or higher is required**

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py

    # Windows
    py -3 -m pip install -U gd.py

gd.py provides an optional *Cython* extension to speed up its parser functions in
`gd.api <https://github.com/NeKitDS/gd.py/blob/master/gd/api>`_ folder,
so make sure that you have *Cython* and *C++ Build Tools* installed.

Development Version
-------------------

You can install stable version of gd.py like this:

.. code:: sh

    $ python3 -m pip install gd.py[dev]

Or you can install development version from GitHub:

.. code:: sh

    $ git clone https://github.com/NeKitDS/gd.py.git
    $ cd gd.py
    $ python3 -m pip install -U .[dev]

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

API
---

gd.py provides server with wrapper around itself, which can be started via a command:

.. code:: sh

    $ python3 -m gd server

Every interaction with the server requires logged in client.

You can login into API system via its endpoint:

.. code:: python

    import requests

    URL = "http://nekit.xyz/api/"  # you can use this server

    data = requests.get(
        URL + "auth/", params={"name": "YOUR_NAME", "password": "YOUR_PASSWORD"}
    ).json()
    token = data["token"]

    print(token)  # "01a2345678b9012345cd6e7fa8bc9cfab01234c56def7a89bc0de1fab234c56d", for example

Credits
-------

Thanks to `Alex1304 <https://github.com/Alex1304>`_ for inspiring the creation of this library.

Credits to `Rapptz <https://github.com/Rapptz>`_ and `discord.py <https://github.com/Rapptz/discord.py>`_ library developers; `tasks <https://github.com/Rapptz/discord.py/blob/master/discord/ext/tasks>`_ package in discord.py is a base for `tasks.py <https://github.com/NeKitDS/gd.py/blob/master/gd/utils/tasks.py>`_ file.

Authors
-------

This project is mainly developed by `NeKitDS <https://github.com/NeKitDS>`_.
Big thanks to `cos8o <https://github.com/cos8o>`_ and `SMJS <https://github.com/SMJSGaming>`_ for helping
to make several requests. Also thanks to `cos8o <https://github.com/cos8o>`_ again for developing `GDCrypto <https://github.com/cos8o/GDCrypto>`_ library,
which was used as a base for `crypto <https://github.com/NeKitDS/gd.py/blob/master/gd/utils/crypto>`_ package.

Links
-----

- `Documentation <https://gdpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/9xhdQFR>`_
- `Geometry Dash Discord Server <https://discord.gg/xkgrP29>`_
