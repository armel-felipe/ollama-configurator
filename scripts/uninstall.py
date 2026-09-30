from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


def _app_data_path() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif os.uname().sysname == "Darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "Ollama Configurator"


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove only Ollama Configurator data.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    app_data = _app_data_path()
    manifest = {
        "app_data_path": str(app_data),
        "preserved_paths": [str(Path.home() / ".ollama" / "models")],
        "status": "dry-run" if not args.apply else "removed",
    }
    if args.apply:
        shutil.rmtree(app_data, ignore_errors=True)
    print(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
