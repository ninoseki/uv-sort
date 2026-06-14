from pathlib import Path

import tomlrt
from tomlrt import Array, Document, Table


def _dependency_key(value: object) -> str:
    return str(value).casefold()


def sort_array(array: Array) -> None:
    """Sort an array of dependencies in place, preserving comments."""
    array.sort(key=_dependency_key)


def sort_table_arrays(table: Table) -> None:
    """Sort every dependency array nested in a table (e.g. optional-dependencies)."""
    for value in table.values():
        if isinstance(value, Array):
            sort_array(value)


def sort_toml_project(text: str) -> Document:
    doc = tomlrt.loads(text)

    # sort dependency arrays
    for path in (("project", "dependencies"), ("tool", "uv", "dev-dependencies")):
        array = doc.get_array(path)
        if array is not None:
            sort_array(array)

    # sort the dependency arrays nested in these tables
    for path in (("project", "optional-dependencies"), ("dependency-groups",)):
        table = doc.get_table(path)
        if table is not None:
            sort_table_arrays(table)

    # sort tool.uv.sources by key
    sources = doc.get_table(("tool", "uv", "sources"))
    if sources is not None:
        sources.sort()

    return doc


def sort(path: Path) -> str:
    return tomlrt.dumps(sort_toml_project(path.read_text()))
