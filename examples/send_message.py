"""Sending messages to friends."""

from getpass import getpass as input_password
from random import choice

from entrypoint import entrypoint
from typing_aliases import AnySet

import gd

FALSE = frozenset(("false", "f", "0", "no", "n"))
TRUE = frozenset(("true", "t", "1", "yes", "y"))
YES = "yes"

CAN_NOT_PARSE = "can not parse `{}` to `bool`"
can_not_parse = CAN_NOT_PARSE.format


def parse_bool(string: str, false: AnySet[str] = FALSE, true: AnySet[str] = TRUE) -> bool:
    string = string.casefold()

    if string in FALSE:
        return False

    if string in TRUE:
        return True

    raise ValueError(can_not_parse(string))


client = gd.Client()

NAME = "name: "
PASSWORD = "password: "

LOGIN_FAILED = "login failed"

NO_FRIENDS = "oh, it seems you have no friends... :("

CONFIRM = "do you want to send a message to `{target.name}`? (Y/n): "
confirm = CONFIRM.format

SUBJECT = "subject: "
CONTENT = "content: "

SENT = "sent the message to `{target.name}`!"
sent = SENT.format

SEND_FAILED = "can not send the message to `{target.name}`"
send_failed = SEND_FAILED.format


async def async_main() -> None:
    name = input(NAME)
    password = input_password(PASSWORD)

    try:
        await client.login(name, password)  # login

    except gd.LoginFailed:  # login failed
        print(LOGIN_FAILED)

        return  # exit

    friends = await client.get_friends().list()  # fetch all friends...

    if not friends:
        print(NO_FRIENDS)

        return  # exit

    # choose target
    target = choice(friends)

    if parse_bool(input(confirm(target=target)) or YES):
        subject = input(SUBJECT)
        content = input(CONTENT)

        try:
            await target.send(subject, content)

        except gd.ClientError:  # if the user has their messages closed or another error occured
            print(send_failed(target=target))

            return

        print(sent(target=target))


@entrypoint(__name__)
def main() -> None:
    client.run(async_main())
