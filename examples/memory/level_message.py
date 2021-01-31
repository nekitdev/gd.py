# type: ignore

"""Example that shows memory reading. Loops are implemented synchronously.
Author: nekitdev
"""

import random
import time

import gd

complete_percent = 100  # do not change
duration = 0.1  # duration to wait between refreshing
memory = gd.memory.get_memory(load=False)  # create memory object, we will load afterwards
messages = [  # some messages to pick from randomly
    "Not 100%",
    "Maybe try jumping?",
    "Too slow!",
    "Problem?",
    "Nice crash",
    "Try again?",
    "Almost...",
    "Rage time!",
    "FeelsSadMan",
    "At least 0%!",
    "BOOM!",
    "So close...",
    "What?!",
    "Are you hurt?",
    "You Died",
    "Game Over",
    "Insert coin",
    "Wrong button",
    "Time's Up!",
    "VAMOS",
    "Nice try",
    "Take a break",
    "Explosion!",
    "Press F to pay respects",
    "RIP.",
    "Get good",
]
previous_level_id = 0
previous_level_name = ""
show_completed = True
show_error = True
show_message = True


def main() -> None:  # we use a function to have nice try ... except
    global previous_level_id, previous_level_name
    global show_completed, show_error, show_message

    while True:
        # reload memory to check if the game is closed
        try:
            memory.reload()
            show_error = True

        except RuntimeError:
            if show_error:
                print("Geometry Dash is closed.")

            show_error = False

            time.sleep(1)

        else:
            if memory.get_level_type() is not gd.api.LevelType.NULL:
                level_id = memory.get_level_id()
                level_name = memory.get_level_name()

                if level_id != previous_level_id and level_name != previous_level_name:
                    print(f"Playing {level_name} (ID: {level_id})")

                previous_level_id = level_id
                previous_level_name = level_name

                mode = "practice" if memory.is_practice_mode() else "normal"

                if memory.is_dead():
                    if show_message:
                        print(f"{random.choice(messages)} ({mode} {memory.get_percent()}%)")

                    show_message = False

                else:
                    show_message = True

                if memory.get_percent() == complete_percent:
                    if show_completed:
                        print(f"Completed {level_name} in {mode} mode (ID: {level_id})")

                    show_completed = False

                else:
                    show_completed = True


try:
    main()

except KeyboardInterrupt:
    pass
