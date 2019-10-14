"""Example of sending a message to a user.
Author: NeKitDS.
"""

import gd
import random  # for fun

client = gd.Client()  # initialize client

# a coro to make things simplier
async def coro():
    # login
    username, password = (
        input('Please enter your GD username: '),
        input('Enter corresponding password: ')
    )
    await client.login(user=username, password=password)

    # get all friends...
    friends = await client.get_friends()

    if not friends:
        print('Oh... Seems like you have no friends in GD...')

    # choose one target
    target = random.choice(friends)

    # send a message to them
    try:
        await target.send(subject='Hello!',
            body='This is a message sent using gd.py library! :)')

        # print that message was successfully sent
        print('Successfully sent a message to {!r}! :)'.format(target))

    # check if an error occured
    except gd.ClientException:  # if a user has their messages closed or other error occured
        print('Failed to send a message to {!r}...'.format(target))


# run a program
client.run(coro())
