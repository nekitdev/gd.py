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

    await song.download("test.mp3", with_bar=True)

Artist Info
-----------

.. autoclass:: ArtistInfo
    :inherited-members:
    :members:

Author
------

.. autoclass:: Author
    :inherited-members:
    :members:

Song
----

.. autoclass:: Song
    :inherited-members:
    :members:
