"""Example that shows downloading a song.
Author: nekitdev.
"""

import gd

client = gd.Client()  # an entry point


async def main() -> None:
    while True:
        query = input("Enter song ID: ")

        try:
            # fetch a song
            song = await client.get_ng_song(int(query))

        except ValueError:
            print("Invalid type. Expected an integer.")

        except gd.MissingAccess:
            print("Song was not found.")

        else:
            name = f"newgrounds_{song.id}.mp3"

            with open(name, "wb") as file:
                await song.download(file=file, with_bar=True)

            print(f"Installed {song.name!r} by {song.author!r} -> {name!r}.")


# gracefully run
try:
    client.run(main())
except KeyboardInterrupt:
    pass
