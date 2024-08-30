from pathlib import Path

import tomlkit
from packaging.requirements import Requirement


def sort_by_name(x: list[str]) -> list[str]:
    _sorted = sorted(x, key=lambda x: Requirement(x).name.casefold())
    item = tomlkit.item(_sorted)
    return item.multiline(True)


def sort_toml_project(text: str) -> tomlkit.TOMLDocument:
    parsed = tomlkit.parse(text)

    dependencies: list[str] | None = parsed.get("project", {}).get("dependencies")
    if dependencies:
        parsed["project"]["dependencies"] = sort_by_name(dependencies)  # type: ignore

    optional_dependencies: dict[str, list[str]] | None = parsed.get("project", {}).get(
        "optional-dependencies"
    )
    if optional_dependencies:
        parsed["project"]["optional-dependencies"] = {  # type: ignore
            k: sort_by_name(v) for k, v in optional_dependencies.items()
        }

    dev_dependencies: list[str] | None = (
        parsed.get("tool", {}).get("uv", {}).get("dev-dependencies")
    )
    if dev_dependencies:
        parsed["tool"]["uv"]["dev-dependencies"] = sort_by_name(dev_dependencies)  # type: ignore

    return parsed


def sort(path: Path) -> str:
    _sorted = sort_toml_project(path.read_text())
    return tomlkit.dumps(_sorted)
