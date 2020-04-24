import gd
import time  # I am sorry ~ nekit

should_error = True
previous_message = ""
memory = None


@gd.tasks.loop(seconds=1)
async def load_memory() -> None:
    global memory, should_error

    # try to fetch process, and print an error on fail
    try:
        memory = gd.memory.get_memory()
        should_error = True
    except RuntimeError:
        if should_error:
            print("Geometry Dash is not open.")
        should_error = False


@gd.tasks.loop(seconds=0.1)
async def get_scene() -> None:
    global previous_message

    if memory is not None:
        scene = memory.get_scene()

        # figure out scene and print things if stuff has changed

        message = f"In scene: {scene}"

        if scene.name.lower() == "editor_or_level":
            message += f" -> ID: {memory.get_level_id()} ({memory.get_attempt()} attempt)"

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
    loop.run_forever()
except KeyboardInterrupt:
    gd.utils.shutdown_loop(loop)
