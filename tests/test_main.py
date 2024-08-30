import pytest

from uv_sort.main import sort_toml_project


@pytest.fixture
def text() -> str:
    return """
[project]
name = "uv-sort"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = ["tomlkit>=0.13.2", "typer>=0.12.5", "pydantic>=2.8.2"]

[project.optional-dependencies]
docs = ["mkdocstrings[python]>=0.25.2", "mkdocs>=1.6.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest-cov>=3.0.0",
    "pytest-pretty>=1.2.0",
    "pytest-randomly>=3.15.0",
    "pytest>=8.3.2",
]
"""


def test_sort(text: str):
    _sorted = sort_toml_project(text)
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
