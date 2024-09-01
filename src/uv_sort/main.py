from pathlib import Path
from typing import cast

import tomlkit
from packaging.requirements import Requirement
from tomlkit.container import Container
from tomlkit.items import Array, Item, Null, Table, _ArrayItemGroup


def sort_array_by_name(x: Array) -> Array:
    def key_builder(y: _ArrayItemGroup) -> str:
        return Requirement(str(y.value)).name.casefold()

    # filter ArrayItemGroup doesn't have a value (e.g. trailing ",")
    filtered = [y for y in x._value if y.value]
    # sort the array
    _sorted = sorted(filtered, key=key_builder)
    # rebuild the array with preserving comments & indentation
    s = "[\n"
    for y in _sorted:
        v = cast(Item, y.value)
        s += "".join(
            [
                x.trivia.indent,
                " " * 4,
                v.value.as_string(),
                ("," if not isinstance(v.value, Null) else ""),
                y.comment.as_string() if y.comment else "",
                "\n",
            ]
        )
    s += x.trivia.indent + "]"

    return tomlkit.array(s).multiline(x._multiline)


def sort_table_by_name(x: Table) -> Table:
    _sorted = Table(
        Container(),
        trivia=x.trivia,
        is_aot_element=x.is_aot_element(),
        is_super_table=x.is_super_table(),
        name=x.name,
        display_name=x.display_name,
    )

    for k, v in x.items():
        v = cast(Array, v)
        _sorted.append(k, sort_array_by_name(v))

    return _sorted


def sort_toml_project(text: str) -> tomlkit.TOMLDocument:
    parsed = tomlkit.parse(text)

    dependencies: Array | None = parsed.get("project", {}).get("dependencies")
    if dependencies:
        parsed["project"]["dependencies"] = sort_array_by_name(dependencies)  # type: ignore

    optional_dependencies: Table | None = parsed.get("project", {}).get(
        "optional-dependencies"
    )
    if optional_dependencies:
        parsed["project"]["optional-dependencies"] = sort_table_by_name(  # type: ignore
            optional_dependencies
        )

    dev_dependencies: Array | None = (
        parsed.get("tool", {}).get("uv", {}).get("dev-dependencies")
    )
    if dev_dependencies:
        parsed["tool"]["uv"]["dev-dependencies"] = sort_array_by_name(dev_dependencies)  # type: ignore

    return parsed


def sort(path: Path) -> str:
    _sorted = sort_toml_project(path.read_text())
    return tomlkit.dumps(_sorted)
