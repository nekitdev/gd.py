gd.py
=====

gd.py is a library that provides its users ability to interact with servers of Geometry Dash.

Key Features
------------

- Modern Pythonic API
- [Future] 100% coverage of the supported Geometry Dash API
- [Future] using ``async`` and ``await``

Installing
----------

**Python 3.5.3 or higher is required**

To install the library with without full image support, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py

    # Windows
    py -3 -m pip install -U gd.py

Otherwise to get image support you should run the following command:
[Not supported on PyPI yet]

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py[image]

    # Windows
    py -3 -m pip install -U gd.py[image]

To install the development version, do the following:

.. code:: sh
    $ git clone https://github.com/NeKitDSS/gd.py
    $ cd gd.py
    $ python3 -m pip install -U .[image]

Optional packages:
~~~~~~~~~~~~~~~~~~

* Pillow (for image support)
* aiohttp [required soon]

Quick example
-------------

.. code:: python

    import gd

    song = gd.client.get_song(633206)
    print(song.name)

    # OUTPUT: Random Song 01

You can find more examples in examples directory.

Links
-----

- `Documentation <https://gdpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/KjehjaC>`_
- `Geometry Dash Discord Server <https://discord.gg/xkgrP29>`_
