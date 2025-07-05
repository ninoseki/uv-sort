from pathlib import Path
from textwrap import dedent

import pytest
from tomlkit import array

from uv_sort.main import sort_array_by_name, sort_toml_project


@pytest.mark.parametrize(
    "raw, expected",
    [
        ('["foo", "bar"]', '["bar", "foo"]'),
        # should be multi-line if there is a line-break
        ('["foo", \n"bar"]', '[ \n"bar","foo",\n]'),
        # should be multi-line if there is a comment
        ('["foo", # baz \n"bar"]', '[\n"bar","foo", # baz \n]'),
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
def test_sort_array_by_name(raw: str, expected: str):
    arr = array(raw)
    _sorted = sort_array_by_name(arr)
    assert _sorted.as_string() == expected


def test_sort_from_file(tmp_path):
    """Test the sort function that reads from a file path"""
    from uv_sort.main import sort

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


@pytest.fixture
def plain() -> str:
    return Path("tests/fixtures/plain/pyproject.toml").read_text()


def test_with_plain(plain: str):
    _sorted = sort_toml_project(plain)

    sorted_dependencies = sorted(["foo", "bar"])

    # array
    assert _sorted["project"]["dependencies"] == sorted_dependencies  # type: ignore
    assert _sorted["tool"]["uv"]["dev-dependencies"] == sorted_dependencies  # type: ignore
    # table
    assert _sorted["project"]["optional-dependencies"] == {"docs": sorted_dependencies}  # type: ignore
    assert _sorted["dependency-groups"] == {"dev": sorted_dependencies}  # type: ignore
    assert _sorted["tool"]["uv"]["sources"] == {  # type: ignore
        "bar": {"git": "https://github.com/ninoseki/bar"},
        "foo": {"git": "https://github.com/ninoseki/foo"},
    }


@pytest.fixture
def comment() -> str:
    return Path("tests/fixtures/with-comment/pyproject.toml").read_text()


def test_with_comment(comment: str):
    _sorted = sort_toml_project(comment)

    sorted_dependencies = sorted(["foo", "bar"])

    assert _sorted["project"]["dependencies"] == sorted_dependencies  # type: ignore
    assert (
        _sorted["project"]["dependencies"].as_string()  # type: ignore
        == '[\n  "bar", # baz\n  "foo",\n]'
    )

    assert _sorted["tool"]["uv"]["dev-dependencies"] == sorted_dependencies  # type: ignore
    assert (
        _sorted["tool"]["uv"]["dev-dependencies"].as_string()  # type: ignore
        == '[\n  "bar", # baz\n  "foo",\n]'
    )

    assert _sorted["project"]["optional-dependencies"] == {"docs": sorted_dependencies}  # type: ignore
    assert (
        _sorted["project"]["optional-dependencies"].as_string()  # type: ignore
        == 'docs = [\n  "bar", # baz\n  "foo",\n]\n\n'
    )

    assert _sorted["dependency-groups"] == {"dev": sorted_dependencies}  # type: ignore
    assert (
        _sorted["dependency-groups"].as_string()  # type: ignore
        == '# baz\ndev = [\n  "bar", # baz\n  "foo",\n]\n'
    )

    assert _sorted["tool"]["uv"]["sources"] == {  # type: ignore
        "bar": {"git": "https://github.com/ninoseki/bar"},
        "foo": {"git": "https://github.com/ninoseki/foo"},
    }
    assert (
        _sorted["tool"]["uv"]["sources"].as_string()  # type: ignore
        == 'bar = { git = "https://github.com/ninoseki/bar" }\nfoo = { git = "https://github.com/ninoseki/foo" }\n\n'
    )
