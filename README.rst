gd.py
=====

.. image:: https://img.shields.io/pypi/v/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: PyPI Library Version

.. image:: https://img.shields.io/pypi/pyversions/gd.py.svg
    :target: https://pypi.python.org/pypi/gd.py
    :alt: Required Python Versions

.. image:: https://readthedocs.org/projects/gdpy/badge/?version=latest
    :target: https://gdpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

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

To install the developer version, run these commands:

.. code:: sh

    $ git clone https://github.com/NeKitDS/gd.py
    $ cd gd.py
    $ python3 -m pip install -U .

Quick example
-------------

.. code:: python

    import gd

    client = gd.Client()
    
    async def test():
        song = await client.get_song(633206)
        print(song.name)

    gd.run(test())

    # OUTPUT: Random Song 01

You can find more examples in examples directory.

Links
-----

- `Documentation <https://gdpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/KjehjaC>`_
- `Geometry Dash Discord Server <https://discord.gg/xkgrP29>`_
