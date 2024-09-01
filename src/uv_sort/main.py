from pathlib import Path
from typing import cast

import tomlkit
from packaging.requirements import Requirement
from tomlkit.container import Container
from tomlkit.items import Array, Table, _ArrayItemGroup


def sort_array_by_name(x: Array) -> Array:
    def key_builder(y: _ArrayItemGroup) -> str:
        return Requirement(str(y.value)).name.casefold()

    # reject ArrayItemGroup doesn't have a value (e.g. trailing ",")
    filtered: list[_ArrayItemGroup] = [item for item in x._value if item.value]
    # sort the array
    _sorted = sorted(filtered, key=key_builder)
    # rebuild the array with preserving comments & indentation
    # consider adding a line-break at last if the last indent has a line-break
    last_indent = _sorted[-1].indent
    has_line_break_at_last = (
        last_indent.as_string() if last_indent else ""
    ).startswith("\n")
    last_line_break = "\n" if has_line_break_at_last else ""

    s = "["
    for item in _sorted:
        # just for type checking
        if item.value is None:
            continue

        s += "".join(
            [
                x.trivia.indent,
                item.indent.as_string() if item.indent else "",
                item.value.as_string(),
                item.comma.as_string() if item.comma else "",
                item.comment.as_string() if item.comment else "",
            ]
        )
    s += x.trivia.indent + last_line_break + "]"

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
