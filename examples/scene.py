import gd
import time  # I am sorry ~ nekit


def main():
    # initialize some variables we might need
    can_error = True
    previous = None

    # start a loop
    while True:
        # attempt to fetch memory object from GD process
        try:
            memory = gd.memory.get_memory()
            can_error = True

        except RuntimeError:
            # failed, print message and wait
            if can_error:
                print("Geometry Dash is not opened.")

            can_error = False
            time.sleep(1)
            continue

        # run checks if a scene has changes
        for _ in range(10):
            # fetch a scene
            scene = memory.get_scene()

            if previous != scene:

                print(f"In scene: {memory.get_scene()}.")

                if scene.name.lower() == "editor_or_level":
                    print(f"-> In level: {memory.get_level_id()}")

                previous = scene

            # sleep a bit
            time.sleep(0.1)


# run main with graceful shutdown
try:
    main()
except KeyboardInterrupt:
    pass
