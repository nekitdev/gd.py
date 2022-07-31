"""An example showing the use of listeners.
Author: nekitdev
"""

import logging

import gd

# enable logging
gd.setup_logging(logging.INFO)

# create a client
client = gd.Client()


# create a listener object and decorate as an event
@client.listen_for("rate")
# implement the listener handling
async def on_rate(level: gd.Level) -> None:
    print(f"New level rated: {level.name} (ID: {level.id})")


# start listening
gd.events.run()
