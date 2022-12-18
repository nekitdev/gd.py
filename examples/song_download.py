"""An example of downloading a song.
Author: nekitdev.
"""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

PROMPT = "song ID ([Ctrl + C] to exit): "

EXPECTED = "expected an integer value, not `{}`"
CAN_NOT_FIND = "can not find a song with ID {}"

NAME = "newgrounds_{}.mp3"

WRITE_BINARY = "wb"

WITH_BAR = True

DOWNLOADED = "downloaded `{}` by `{}` -> `{}`"


async def async_main() -> None:
    while True:
        query = input(PROMPT)

        try:
            song_id = int(query)

        except ValueError:
            print(EXPECTED.format(query))

        else:
            try:
                # fetch a song
                song = await client.get_newgrounds_song(int(query))

            except gd.GDError:
                print(CAN_NOT_FIND.format(song_id))

            else:
                name = NAME.format(song.id)

                with open(name, WRITE_BINARY) as file:
                    await song.download(file, with_bar=WITH_BAR)

                print(DOWNLOADED.format(song.name, song.artist.name, name))


@entrypoint(__name__)
def main() -> None:
    try:
        client.run(async_main())

    except KeyboardInterrupt:
        return
