from pathlib import Path
from secrets import token_hex
from subprocess import call
from sys import executable as INTERPRETER_STRING
from typing import Any, Dict, Sequence, TypeVar
from zipfile import ZipFile

from entrypoint import entrypoint

Namespace = Dict[str, Any]

S = TypeVar("S", bound=Namespace)

INTERPRETER_PATH = Path(INTERPRETER_STRING)

ROOT = Path(__file__).parent

SHARED_OBJECT = ".so"
PYTHON_DLL = ".pyd"

EXTENSIONS = frozenset((SHARED_OBJECT, PYTHON_DLL))

POETRY = "poetry"
RUN = "run"
MATURIN = "maturin"
BUILD = "build"
INTERPRETER = "-i"
OUTPUT = "-o"
RELEASE = "-r"

WHEELS = "wheels"
WHEEL = ".whl"

TOKEN_SIZE = 16
TOKEN = token_hex(TOKEN_SIZE)

OUTPUT_PATH = ROOT / WHEELS / TOKEN

FAILED_TO_FIND_EXTENSIONS = "failed to find extensions"


def build_command(output_path: Path) -> Sequence[str]:
    return (
        POETRY,
        RUN,
        MATURIN,
        BUILD,
        RELEASE,
        INTERPRETER,
        INTERPRETER_PATH.as_posix(),
        OUTPUT,
        output_path.as_posix(),
    )


def build(setup_keywords: S, output_path: Path = OUTPUT_PATH) -> S:
    result = call(build_command(output_path))

    if result:
        return setup_keywords

    wheel = WHEEL
    extensions = EXTENSIONS

    result_path = ROOT

    for path in output_path.iterdir():
        if path.suffix == wheel:
            with ZipFile(path) as zip_file:
                for archive_path in map(Path, zip_file.namelist()):
                    if archive_path.suffix in extensions:
                        zip_file.extract(archive_path.as_posix(), result_path)
                        break

                else:
                    raise LookupError(FAILED_TO_FIND_EXTENSIONS)

                break

    else:
        raise LookupError(FAILED_TO_FIND_EXTENSIONS)

    return setup_keywords


@entrypoint(__name__)
def main() -> None:
    build({})  # type: ignore
