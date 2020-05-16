"""Somewhat useful 'python -m gd' implementation"""

import argparse
import sys
import pkg_resources
import platform

import aiohttp
import gd


def show_version() -> None:
    entries = []

    entries.append(
        "- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(sys.version_info)
    )

    version_info = gd.version_info
    entries.append("- gd.py v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(version_info))

    if version_info.releaselevel != "final":
        pkg = pkg_resources.get_distribution("gd.py")
        if pkg:
            entries.append("    - gd.py pkg_resources: v{0}".format(pkg.version))

    entries.append("- [gd_console] v0.4.0")

    entries.append(f"- aiohttp v{aiohttp.__version__}")

    uname = platform.uname()
    entries.append("- System Info: {0.system} {0.release} {0.version}".format(uname))

    print("\n".join(entries))


def main() -> None:
    parser = argparse.ArgumentParser(description="gd.py console commands", prog="gd")

    parser.add_argument(
        "-v",
        "--version",
        help="show versions (gd.py, python, etc.)",
        action="store_true",
        default=False,
    )
    parser.add_argument("action", help="run a given action (console, server)", nargs="?")

    parsed = parser.parse_args()

    if parsed.version:
        show_version()

    if not parsed.action:
        return

    action = parsed.action.lower()

    if action == "console":
        from IPython import start_ipython

        start_ipython([])

    elif action == "server":
        gd.server.start()

    else:
        print(f"Invalid action: {action!r}.")


# run main
if __name__ == "__main__":
    main()
