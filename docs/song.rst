.. currentmodule:: gd

Songs
=====

All levels in Geometry Dash are based on different songs;
either official ones, or custom songs from Newgrounds.

gd.py provides simple API for fetching and working with both of them::

    client = gd.Client()

    song = gd.Song.official(0, client=client)
    # <Song id=0 name='Stereo Madness' author='ForeverBound'>

    print(song.is_custom())  # False

    song = await client.get_song(1)  # or get_ng_song for Newgrounds fetching
    # <Song id=1 name='Chilled 1' author='Recoil'>

    data = await song.download()  # returns song data, as bytes

    with open('test.mp3', 'wb') as file:
        file.write(data)

Artist Info
-----------

.. autoclass:: ArtistInfo
    :members:

Author
------

.. autoclass:: Author
    :members:

Song
----

.. autoclass:: Song
    :members:
