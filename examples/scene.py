import gd
import time  # I am sorry ~ nekit


def main():
    can_error = True
    previous = None

    while True:
        try:
            memory = gd.memory.get_memory()
            can_error = True

        except RuntimeError:
            if can_error:
                print("Geometry Dash is not opened.")
            can_error = False
            time.sleep(1)
            continue

        for _ in range(10):
            scene = memory.get_scene()

            if previous != scene:

                print(f"In scene: {memory.get_scene()}.")

                if scene.name.lower() == "editor_or_level":
                    print(f"-> In level: {memory.get_level_id()}")

                previous = scene

            time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    pass
