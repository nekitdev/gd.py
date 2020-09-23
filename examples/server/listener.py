"""An example showing the use of listeners.
Author: nekitdev
"""

import gd

# enable logging
gd.setup_logging()

# create a client
client = gd.Client()


# create a listener object and decorate as an event
@client.listen_for("rate")
# implement the listener handling
async def on_level_rated(level: gd.Level) -> None:
    print(f"New level rated: {level}")


# start listening
gd.events.run()
