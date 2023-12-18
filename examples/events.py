"""Using listeners to handle events."""

from entrypoint import entrypoint

import gd

client = gd.Client()  # initialize the client

RATED = "new level rated: {level.name} (ID: {level.id})"
rated = RATED.format


@client.event  # decorate the handler
async def on_rate(level: gd.Level) -> None:
    print(rated(level=level))


client.listen_for_rate()  # listen for the `rate` event


@entrypoint(__name__)
def main() -> None:
    client.create_controller().run()  # create the controller and run it
