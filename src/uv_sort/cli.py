from pathlib import Path
from typing import Annotated

import typer

from . import main

app = typer.Typer()


@app.command()
def sort(
    path: Annotated[
        list[str],
        typer.Argument(help="pyproject.toml path(s) to sort"),
    ],
):
    for _path in path:
        p = Path(_path)

        _sorted = main.sort(p)
        if p.read_text() == _sorted:
            continue

        p.write_text(_sorted)


if __name__ == "__main__":
    typer.run(app())
