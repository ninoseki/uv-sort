# uv-sort

[![PyPI version](https://badge.fury.io/py/uv-sort.svg)](https://badge.fury.io/py/uv-sort)

Sort uv's dependencies alphabetically.

## Installation

```bash
pip install uv-sort
# or
uv add uv-sort
```

## Usage

```bash
$ uv-sort --help

 Usage: uv-sort [OPTIONS] PATH...

$ uv-sort pyproject.toml
```

## pre-commit

```yaml
repos:
  - repo: https://github.com/ninoseki/uv-sort
    rev: "" # Use the sha / tag you want to point at
    hooks:
      - id: uv-sort
```

## lefthook

```yaml
pre-commit:
  commands:
    uv-sort:
      run: uv-sort {staged_files}
      glob: "pyproject.toml"
```
