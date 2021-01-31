# type: ignore

"""Example that shows simple memory reading. Task loops are implemented asynchronously.
Author: nekitdev
"""

import gd

memory = None
previous_message = ""
should_error = True


@gd.tasks.loop(seconds=1)
async def load_memory() -> None:
    global memory, should_error

    # try to fetch process, and print an error on fail
    try:
        memory = gd.memory.get_memory()

        should_error = True

    except RuntimeError:
        memory = None

        if should_error:
            print("Geometry Dash is not open.")

        should_error = False


@gd.tasks.loop(seconds=0.1)
async def get_scene() -> None:
    global previous_message

    if memory is not None:
        scene = memory.get_scene()

        # figure out scene and print things if stuff has changed

        message = f"In scene: {scene.title}"

        if previous_message != message:
            print(message)
            previous_message = message


# start task loops
load_memory.start()
get_scene.start()

# get a loop
loop = gd.utils.acquire_loop()

# run main with graceful shutdown
try:
    gd.events.run(loop)

except KeyboardInterrupt:
    gd.utils.shutdown_loop(loop)
