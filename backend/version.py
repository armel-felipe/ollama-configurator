from __future__ import annotations

import os
import re
import sys
from pathlib import Path


_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def read_version_file(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1 or not _SEMVER.fullmatch(lines[0]):
        raise ValueError(f"invalid application version in {path}")
    return lines[0]


def get_version() -> str:
    override = os.environ.get("OLLAMA_CONFIGURATOR_VERSION")
    if override:
        if not _SEMVER.fullmatch(override):
            raise ValueError("invalid OLLAMA_CONFIGURATOR_VERSION")
        return override

    candidates = [
        Path(__file__).resolve().parents[1] / "VERSION",
        Path(getattr(sys, "_MEIPASS", "")) / "VERSION",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return read_version_file(candidate)
    raise RuntimeError("application VERSION file is unavailable")
