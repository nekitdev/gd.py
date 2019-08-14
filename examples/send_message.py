"""Example of sending a message to a user.
Author: NeKitDS.
"""

import gd
import random  # for fun

client = gd.Client()  # initialize client

gd.utils.run(
    client.login(user='Username', password='YourP4ssw0rd')
)  # login with given credentials

# a coro to make things simplier
async def coro():
    # get all friends...
    friends = await client.get_friends()
    # choose one target
    target = random.choice(friends)
    # send a message to them
    try:
        await target.send(subject='Hello!',
            message='This is a message sent using gd.py library! :)')
        # print that message was successfully sent
        print(f'Successfully sent a message to {target!r}!')
    # check if an error occured
    except gd.ClientException:  # if a user has their messages closed or other error occured
        print(f'Failed to send a message to {target!r}...')

# run a program
gd.utils.run(coro())
