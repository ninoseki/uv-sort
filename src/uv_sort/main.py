from pathlib import Path

import tomlrt
from tomlrt import Array, Document, Table

NAME_FIELDS = ("package", "requirement")
DEPENDENCY_ARRAY_PATHS = (
    ("project", "dependencies"),
    ("build-system", "requires"),
    ("tool", "uv", "dev-dependencies"),
    ("tool", "uv", "constraint-dependencies"),
    ("tool", "uv", "build-constraint-dependencies"),
    ("tool", "uv", "override-dependencies"),
    ("tool", "uv", "exclude-dependencies"),
)
DEPENDENCY_TABLE_PATHS = (
    ("project", "optional-dependencies"),
    ("dependency-groups",),
    ("tool", "uv", "extra-build-dependencies"),
)
KEY_SORTED_TABLE_PATHS = (
    ("tool", "uv", "sources"),
    ("tool", "uv", "extra-build-dependencies"),
)


def _dependency_key(value: object) -> str:
    """Build a sort key, falling back to the dependency name of an inline table."""
    if isinstance(value, Table):
        for field in NAME_FIELDS:
            name = value.get(field)
            if isinstance(name, str):
                return name.casefold()

    return str(value).casefold()


def sort_array(array: Array) -> None:
    """Sort an array of dependencies in place, preserving comments."""
    array.sort(key=_dependency_key)

    # a per-package entry (e.g. in override-dependencies) nests its own array
    for value in array:
        if isinstance(value, Table):
            nested = value.get_array("dependencies")
            if nested is not None:
                nested.sort(key=_dependency_key)


def sort_table_arrays(table: Table) -> None:
    """Sort every dependency array nested in a table (e.g. optional-dependencies)."""
    for value in table.values():
        if isinstance(value, Array):
            sort_array(value)


def sort_toml_project(text: str) -> Document:
    doc = tomlrt.loads(text)

    # sort dependency arrays
    for path in DEPENDENCY_ARRAY_PATHS:
        array = doc.get_array(path)
        if array is not None:
            sort_array(array)

    # sort the dependency arrays nested in these tables
    for path in DEPENDENCY_TABLE_PATHS:
        table = doc.get_table(path)
        if table is not None:
            sort_table_arrays(table)

    # sort these tables by key
    for path in KEY_SORTED_TABLE_PATHS:
        table = doc.get_table(path)
        if table is not None:
            table.sort()

    return doc


def sort(path: Path) -> str:
    return tomlrt.dumps(sort_toml_project(path.read_text()))
