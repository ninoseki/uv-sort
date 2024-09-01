from pathlib import Path

import pytest

from uv_sort.main import sort_toml_project


@pytest.fixture
def plain() -> str:
    return Path("tests/fixtures/plain/pyproject.toml").read_text()


def test_with_plain(plain: str):
    _sorted = sort_toml_project(plain)

    assert _sorted["project"]["dependencies"] == [  # type: ignore
        "pydantic>=2.8.2",
        "tomlkit>=0.13.2",
        "typer>=0.12.5",
    ]
    assert _sorted["project"]["optional-dependencies"] == {  # type: ignore
        "docs": ["mkdocs>=1.6.0", "mkdocstrings[python]>=0.25.2"]
    }
    assert _sorted["tool"]["uv"]["dev-dependencies"] == [  # type: ignore
        "pytest>=8.3.2",
        "pytest-cov>=3.0.0",
        "pytest-pretty>=1.2.0",
        "pytest-randomly>=3.15.0",
    ]


@pytest.fixture
def comment() -> str:
    return Path("tests/fixtures/with-comment/pyproject.toml").read_text()


def test_with_comment(comment: str):
    _sorted = sort_toml_project(comment)
    assert _sorted["project"]["dependencies"] == [  # type: ignore
        "pydantic>=2.8.2",
        "tomlkit>=0.13.2",
        "typer>=0.12.5",
    ]

    assert (
        '  "pydantic>=2.8.2", # foo!' in _sorted["project"]["dependencies"].as_string()  # type: ignore
    )

    assert _sorted["project"]["optional-dependencies"] == {  # type: ignore
        "docs": ["mkdocs>=1.6.0", "mkdocstrings[python]>=0.25.2"]
    }
    assert (
        '  "mkdocs>=1.6.0",                # bar!'
        in _sorted["project"]["optional-dependencies"].as_string()  # type: ignore
    )

    assert _sorted["tool"]["uv"]["dev-dependencies"] == [  # type: ignore
        "pytest>=8.3.2",
        "pytest-cov>=3.0.0",
        "pytest-pretty>=1.2.0",
        "pytest-randomly>=3.15.0",
    ]
    assert (
        '  "pytest>=8.3.2",           # baz!'
        in _sorted["tool"]["uv"]["dev-dependencies"].as_string()  # type: ignore
    )
