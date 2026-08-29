from pathlib import Path
from textwrap import dedent

import pytest
import tomlrt

from uv_sort.main import _dependency_key, sort, sort_array, sort_toml_project


def _sort_array_string(raw: str) -> str:
    doc = tomlrt.loads(f"x = {raw}")
    array = doc.array("x")
    sort_array(array)
    return tomlrt.dumps(doc).removeprefix("x = ")


@pytest.mark.parametrize(
    "raw, expected",
    [
        ('["foo", "bar"]', '["bar", "foo"]'),
        # should be multi-line if there is a line-break
        ('["foo", \n"bar"]', '["bar", \n"foo"]'),
        # should be multi-line if there is a comment
        ('["foo", # baz \n"bar"]', '["bar",\n"foo" # baz \n]'),
        # should be intact if it only has one element
        ('["foo" # bar\n]', '["foo" # bar\n]'),
        # ref. https://github.com/ninoseki/uv-sort/issues/18
        (
            '["dvc-pandas>=0.3.3", "dvc[azure]>=3.59.2", "uv-sort>=0.5.1"]',
            '["dvc-pandas>=0.3.3", "dvc[azure]>=3.59.2", "uv-sort>=0.5.1"]',
        ),
        # standalone comments should be preserved with their following dependency
        (
            '[\n"zoo",\n# comment about bar\n"bar",\n"foo",\n]',
            '[\n# comment about bar\n"bar",\n"foo",\n"zoo",\n]',
        ),
        # multiple standalone comments should stay together
        (
            '[\n"zoo",\n# first comment\n# second comment\n"bar",\n]',
            '[\n# first comment\n# second comment\n"bar",\n"zoo",\n]',
        ),
        # mixed inline and standalone comments
        (
            '[\n"zoo", # inline comment\n# standalone comment\n"bar",\n"foo", # another inline\n]',
            '[\n# standalone comment\n"bar",\n"foo", # another inline\n"zoo", # inline comment\n]',
        ),
        # trailing comments should be preserved
        (
            '[\n"zoo",\n"bar",\n# trailing comment\n]',
            '[\n"bar",\n"zoo",\n# trailing comment\n]',
        ),
    ],
)
def test_sort_array(raw: str, expected: str):
    assert _sort_array_string(raw) == expected


def test_sort_from_file(tmp_path):
    """Test the sort function that reads from a file path"""
    toml_content = dedent("""\
        [project]
        dependencies = [
            "zebra",
            "alpha",
        ]
        """)

    test_file = tmp_path / "test.toml"
    test_file.write_text(toml_content)

    result = sort(test_file)
    assert "alpha" in result
    assert "zebra" in result


def test_with_plain():
    plain = Path("tests/fixtures/plain/pyproject.toml").read_text()
    expected = dedent("""\
        [project]
        name = "dummy"
        version = "0.1.0"
        description = "dummy"
        readme = "README.md"
        requires-python = ">=3.12"
        dependencies = ["bar", "foo"]

        [project.optional-dependencies]
        docs = ["bar", "foo"]

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.uv]
        dev-dependencies = ["bar", "foo"]

        [tool.uv.sources]
        bar = { git = "https://github.com/ninoseki/bar" }
        foo = { git = "https://github.com/ninoseki/foo" }

        [dependency-groups]
        dev = ["bar", "foo"]
        """)
    assert tomlrt.dumps(sort_toml_project(plain)) == expected


def test_with_comment():
    comment = Path("tests/fixtures/with-comment/pyproject.toml").read_text()
    expected = dedent("""\
        [project]
        name = "dummy"
        version = "0.1.0"
        description = "..."
        readme = "README.md"
        requires-python = ">=3.12"
        dependencies = [
          "bar", # baz
          "foo",
        ]

        [project.optional-dependencies]
        docs = [
          "bar", # baz
          "foo",
        ]

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.uv]
        dev-dependencies = [
          "bar", # baz
          "foo",
        ]

        [tool.uv.sources]
        bar = { git = "https://github.com/ninoseki/bar" }
        foo = { git = "https://github.com/ninoseki/foo" }

        [dependency-groups]
        # baz
        dev = [
          "bar", # baz
          "foo",
        ]
        """)
    assert tomlrt.dumps(sort_toml_project(comment)) == expected


def test_with_uv_sections():
    """tool.uv's dependency sections and build-system.requires are sorted."""
    raw = dedent("""\
        [project]
        dependencies = ["zoo", "aa"]

        [build-system]
        requires = ["zzz-backend", "hatchling"]
        build-backend = "hatchling.build"

        [tool.uv]
        constraint-dependencies = ["werkzeug==2.3.0", "anyio>=4"]
        build-constraint-dependencies = ["setuptools>=40", "cmake<4"]
        override-dependencies = ["werkzeug==2.3.0", { package = "flask", dependencies = ["z", "a"] }, "aa"]
        exclude-dependencies = [{ package = "zulu", dependencies = ["x"] }, "boto3"]

        [tool.uv.extra-build-dependencies]
        zope = ["setuptools", "cython"]
        apache-airflow = [{ requirement = "numpy", match-runtime = true }, "wheel"]
        """)
    expected = dedent("""\
        [project]
        dependencies = ["aa", "zoo"]

        [build-system]
        requires = ["hatchling", "zzz-backend"]
        build-backend = "hatchling.build"

        [tool.uv]
        constraint-dependencies = ["anyio>=4", "werkzeug==2.3.0"]
        build-constraint-dependencies = ["cmake<4", "setuptools>=40"]
        override-dependencies = ["aa", { package = "flask", dependencies = ["a", "z"] }, "werkzeug==2.3.0"]
        exclude-dependencies = ["boto3", { package = "zulu", dependencies = ["x"] }]

        [tool.uv.extra-build-dependencies]
        apache-airflow = [{ requirement = "numpy", match-runtime = true }, "wheel"]
        zope = ["cython", "setuptools"]
        """)
    assert tomlrt.dumps(sort_toml_project(raw)) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        # an inline table is keyed by its dependency name, not its repr
        ('{ package = "flask" }', "flask"),
        ('{ requirement = "numpy", match-runtime = true }', "numpy"),
        # a plain requirement falls back to the string itself
        ('"Flask>=3"', "flask>=3"),
    ],
)
def test_dependency_key(value: str, expected: str):
    doc = tomlrt.loads(f"x = [{value}]")
    assert _dependency_key(doc.array("x")[0]) == expected
