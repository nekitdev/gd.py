"""Downloading songs."""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

PROMPT = "song ID ([Ctrl + C] to exit): "

EXPECTED = "expected an integer value, not `{query}`"
expected = EXPECTED.format

NOT_FOUND = "song with ID `{song_id}` not found"
not_found = NOT_FOUND.format

SONG_NAME = "newgrounds_{song.id}.mp3"
song_name = SONG_NAME.format

WITH_BAR = True

DOWNLOADED = "downloaded `{song.name}` by `{song.artist.name}` -> `{name}`"
downloaded = DOWNLOADED.format

EXITING = "exiting..."


async def async_main() -> None:
    while True:
        query = input(PROMPT)

        try:
            song_id = int(query)

        except ValueError:
            print(expected(query=query))

        else:
            try:
                # fetch a song
                song = await client.get_newgrounds_song(song_id)

            except gd.GDError:
                print(not_found(song_id=song_id))

            else:
                name = song_name(song=song)

                await song.download_to(name, with_bar=WITH_BAR)

                print(downloaded(song=song, name=name))


@entrypoint(__name__)
def main() -> None:
    try:
        client.run(async_main())

    except KeyboardInterrupt:
        print(EXITING)

