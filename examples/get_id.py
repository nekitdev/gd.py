"""Simple example showing user searching.
Author: NeKitDS
"""

import asyncio
import gd

client = gd.Client()

async def main():
    # get some input from user
    name = input('Enter your GD nickname: ')

    # look up and print IDs if found
    try:
        user = await client.find_user(name)

        if isinstance(user, gd.UnregisteredUser):
            print('Hey there, {0.name}! Seems like you are unregistered...'.format(user))

        else:
            print('Hello, {0.name}! Your AccountID is {0.account_id} and PlayerID is {0.id}.'.format(user))

    # could not find
    except gd.MissingAccess:
        print('Sorry, could not find user with name {}...'.format(name))

    # let us wait a bit before exiting
    await asyncio.sleep(3)

# run a program
client.run(main())
