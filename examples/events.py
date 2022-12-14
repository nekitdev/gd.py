"""An example showing the use of listeners.
Author: nekitdev
"""

from entrypoint import entrypoint
import gd

client = gd.Client()  # initialize the client

RATED = "new level rated: {level.name} (ID: {level.id})"


@client.event  # create a listener and decorate the handler
async def on_rate(level: gd.Level) -> None:
    print(RATED.format(level=level))


client.listen_for_rate()  # subscribe to the `rate` event


@entrypoint(__name__)
def main() -> None:
    client.create_controller().run()  # create a controller and run it
