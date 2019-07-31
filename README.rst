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

To install the library, you can just run the following command:

.. code:: sh

    # Linux/OS X
    python3 -m pip install -U gd.py

    # Windows
    py -3 -m pip install -U gd.py

To install the developer version, run these commands:

.. code:: sh

    $ git clone https://github.com/NeKitDSS/gd.py
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

    gd.utils.run(test())

    # OUTPUT: Random Song 01

You can find more examples in examples directory.

Links
-----

- `Documentation [Empty] <https://gdpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server [Not ready yet] <https://discord.gg/KjehjaC>`_
- `Geometry Dash Discord Server <https://discord.gg/xkgrP29>`_
