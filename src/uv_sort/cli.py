import sys
from pathlib import Path
from typing import Annotated

import typer

from . import main

app = typer.Typer()


@app.command()
def sort(
    path: Annotated[
        list[str] | None,
        typer.Argument(
            help="pyproject.toml path(s) to sort. Defaults to pyproject.toml.",
        ),
    ] = None,
    check: Annotated[
        bool,
        typer.Option(
            help="Check if dependencies are sorted and exit with a non-zero status code when they are not.",  # noqa: E501
        ),
    ] = False,
):
    path = path or ["pyproject.toml"]
    for _path in path:
        p = Path(_path)

        _sorted = main.sort(p)
        if p.read_text() == _sorted:
            continue

        if check:
            print(f"{_path}'s dependencies are not sorted", file=sys.stderr)  # noqa: T201
            sys.exit(1)

        p.write_text(_sorted)


if __name__ == "__main__":
    typer.run(app())
