import sys
from pathlib import Path
from typing import Annotated, Optional

import typer

from . import main

app = typer.Typer()


@app.command()
def sort(
    path: Annotated[
        Optional[list[Path]],
        typer.Argument(
            help="pyproject.toml path(s) to sort. Defaults to pyproject.toml.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            help="Output the modified file to stdout without modifying the file.",
        ),
    ] = False,
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            "-c",
            help="Check if dependencies are sorted and exit with a non-zero status code when they are not.",  # noqa: E501
        ),
    ] = False,
):
    path = path or [Path("pyproject.toml")]
    for p in path:
        _sorted = main.sort(p)
        if p.read_text() == _sorted:
            continue

        if check:
            print(f"{p}'s dependencies are not sorted", file=sys.stderr)  # noqa: T201
            sys.exit(1)

        if dry_run:
            print(_sorted)  # noqa: T201
            continue

        p.write_text(_sorted)


if __name__ == "__main__":
    typer.run(app())
