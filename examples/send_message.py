"""An example of sending a message to a friend.
Author: nekitdev.
"""

import random  # for fun
from getpass import getpass as input_password
from typing import AbstractSet

from entrypoint import entrypoint

import gd

FALSE = frozenset(("false", "f", "0", "no", "n"))
TRUE = frozenset(("true", "t", "1", "yes", "y"))
YES = "yes"

CAN_NOT_PARSE = "can not parse `{}` to bool"


def parse_bool(string: str, false: AbstractSet[str] = FALSE, true: AbstractSet[str] = TRUE) -> bool:
    string = string.casefold()

    if string in FALSE:
        return False

    if string in TRUE:
        return True

    raise ValueError(CAN_NOT_PARSE.format(string))


client = gd.Client()

NAME = "name: "
PASSWORD = "password: "

LOGIN_FAILED = "login failed..."

NO_FRIENDS = "oh, it seems you have no friends... :("

CONFIRM = "do you want to send a message to `{target.name}`? (Y/n)"

SUBJECT = "subject: "
CONTENT = "content: "

SENT = "sent the message to `{target.name}`!"
CAN_NOT_SEND = "can not send the message to `{target.name}`"


async def async_main() -> None:
    name = input(NAME)
    password = input_password(PASSWORD)

    try:
        await client.login(name, password)  # login

    except gd.LoginFailed:  # login failed
        print(LOGIN_FAILED)

        return

    friends = await client.get_friends().list()  # fetch all friends...

    if not friends:
        print(NO_FRIENDS)

        return  # exit

    # choose target
    target = random.choice(friends)

    if parse_bool(input(CONFIRM.format(target=target)) or YES):
        try:
            subject = input(SUBJECT)
            content = input(CONTENT)

            await target.send(subject, content)

            print(SENT.format(target=target))

        except gd.ClientError:  # if the user has their messages closed or another error occured
            print(CAN_NOT_SEND.format(target=target))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
