"""Example that shows getting current daily/weekly levels.
Author: NeKitDS.
"""

import gd

client = gd.Client()  # an entry point to gd API

# let's create one coroutine to use
# run() only once.

async def coro():
    # getting daily...
    daily = await client.get_daily()

    # getting weekly...
    weekly = await client.get_weekly()

    # now let's print...
    info = ('Current daily level: {!r}.'.format(daily), 'Current weekly demon: {!r}.'.format(weekly))

    for piece in info:
        print(piece)

# run a coroutine
client.run(coro())
