"""Test standalone comment preservation functionality"""

from textwrap import dedent

import pytest
import tomlkit

from uv_sort.main import sort_toml_project


@pytest.mark.parametrize(
    "test_name, input_toml, expected_toml",
    [
        (
            "basic_standalone_comment",
            dedent("""\
                [project]
                dependencies = [
                    "zoo",
                    # This comment is about bar
                    "bar",
                    "apple",
                ]
                """),
            dedent("""\
                [project]
                dependencies = [
                    "apple",
                    # This comment is about bar
                    "bar",
                    "zoo",
                ]
                """),
        ),
        (
            "multiple_comments_for_one_dependency",
            dedent("""\
                [project]
                dependencies = [
                    "zebra",
                    # First comment about alpha
                    # Second comment about alpha
                    # Third comment about alpha
                    "alpha",
                    "beta",
                ]
                """),
            dedent("""\
                [project]
                dependencies = [
                    # First comment about alpha
                    # Second comment about alpha
                    # Third comment about alpha
                    "alpha",
                    "beta",
                    "zebra",
                ]
                """),
        ),
        (
            "mixed_inline_and_standalone",
            dedent("""\
                [project]
                dependencies = [
                    "zebra",  # inline comment for zebra
                    # standalone comment for alpha
                    "alpha",
                    "gamma",  # inline comment for gamma
                    # standalone comment for beta
                    "beta",  # also has inline comment
                ]
                """),
            dedent("""\
                [project]
                dependencies = [
                    # standalone comment for alpha
                    "alpha",
                    # standalone comment for beta
                    "beta",  # also has inline comment
                    "gamma",  # inline comment for gamma
                    "zebra",  # inline comment for zebra
                ]
                """),
        ),
        (
            "dev_dependencies",
            dedent("""\
                [tool.uv]
                dev-dependencies = [
                    "ruff",
                    # For testing with coverage
                    "pytest-cov",
                    # For basic testing
                    "pytest",
                ]
                """),
            dedent("""\
                [tool.uv]
                dev-dependencies = [
                    # For basic testing
                    "pytest",
                    # For testing with coverage
                    "pytest-cov",
                    "ruff",
                ]
                """),
        ),
        (
            "optional_dependencies",
            dedent("""\
                [project.optional-dependencies]
                docs = [
                    "sphinx",
                    # Theme for documentation
                    "sphinx-rtd-theme",
                    "myst-parser",
                ]
                """),
            dedent("""\
                [project.optional-dependencies]
                docs = [
                    "myst-parser",
                    "sphinx",
                    # Theme for documentation
                    "sphinx-rtd-theme",
                ]
                """),
        ),
        (
            "dependency_groups",
            dedent("""\
                [dependency-groups]
                test = [
                    "pytest",
                    # Coverage tool
                    "coverage",
                    "hypothesis",
                ]
                """),
            dedent("""\
                [dependency-groups]
                test = [
                    # Coverage tool
                    "coverage",
                    "hypothesis",
                    "pytest",
                ]
                """),
        ),
        (
            "trailing_comments",
            dedent("""\
                [project]
                dependencies = [
                    "zebra",
                    "alpha",
                    # This is a trailing comment
                    # Second trailing comment
                ]
                """),
            dedent("""\
                [project]
                dependencies = [
                    "alpha",
                    "zebra",
                    # This is a trailing comment
                    # Second trailing comment
                ]
                """),
        ),
    ],
)
def test_standalone_comment_preservation(
    test_name: str, input_toml: str, expected_toml: str
):
    """Test that standalone comments are preserved and stay with their following dependency"""
    sorted_doc = sort_toml_project(input_toml)
    result = tomlkit.dumps(sorted_doc)
    assert result == expected_toml, f"Failed test: {test_name}"


def test_complex_scenario():
    """Test a complex scenario with various comment types"""
    input_toml = dedent("""\
        [project]
        name = "test-project"
        dependencies = [
            "requests",  # HTTP library
            # Database dependencies
            # These are critical for the app
            "sqlalchemy",
            "psycopg2",  # PostgreSQL adapter
            # Web framework and extensions
            "flask",
            # Authentication
            # Used for user management
            # Very important!
            "flask-login",
            "werkzeug",  # WSGI utilities
        ]

        [tool.uv]
        dev-dependencies = [
            # Testing tools
            "pytest",
            # Code quality
            "black",
            "ruff",  # Fast linter
        ]
        """)

    expected_toml = dedent("""\
        [project]
        name = "test-project"
        dependencies = [
            # Web framework and extensions
            "flask",
            # Authentication
            # Used for user management
            # Very important!
            "flask-login",
            "psycopg2",  # PostgreSQL adapter
            "requests",  # HTTP library
            # Database dependencies
            # These are critical for the app
            "sqlalchemy",
            "werkzeug",  # WSGI utilities
        ]

        [tool.uv]
        dev-dependencies = [
            # Code quality
            "black",
            # Testing tools
            "pytest",
            "ruff",  # Fast linter
        ]
        """)

    sorted_doc = sort_toml_project(input_toml)
    result = tomlkit.dumps(sorted_doc)
    assert result == expected_toml
