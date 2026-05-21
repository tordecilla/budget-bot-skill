#!/usr/bin/env python
"""Sync canonical Budget Bot skill files into the Codex plugin wrapper."""

from __future__ import annotations

import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT.parents[1]
PLUGIN_SKILL = PLUGIN_ROOT / "skills" / "budget-bot"

FILES = [
    "SKILL.md",
    "README.md",
]

DIRS = [
    "scripts",
    "references",
]


def copy_file(relative_path: str) -> None:
    source = SKILL_ROOT / relative_path
    destination = PLUGIN_SKILL / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_dir(relative_path: str) -> None:
    source = SKILL_ROOT / relative_path
    destination = PLUGIN_SKILL / relative_path
    destination.mkdir(parents=True, exist_ok=True)
    for source_file in source.rglob("*"):
        if source_file.is_dir() or "__pycache__" in source_file.parts or source_file.suffix == ".pyc":
            continue
        relative_file = source_file.relative_to(source)
        destination_file = destination / relative_file
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)


def main() -> None:
    PLUGIN_SKILL.mkdir(parents=True, exist_ok=True)
    for relative_path in FILES:
        copy_file(relative_path)
    for relative_path in DIRS:
        copy_dir(relative_path)
    print(f"Synced skill files into {PLUGIN_SKILL}")


if __name__ == "__main__":
    main()
