from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "0.1.0.dev0"


def _manifest() -> dict[str, object]:
    return {
        "artifact": "OllamaConfiguratorBackend",
        "version": os.environ.get("OLLAMA_CONFIGURATOR_VERSION", DEFAULT_VERSION),
        "bind_host": "127.0.0.1",
        "ports": {"api": 8787, "gateway": 11435},
        "entrypoint": "backend.__main__",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Ollama Configurator backend.")
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "backend")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = _manifest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    if args.dry_run:
        print(json.dumps(manifest))
        return 0

    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller is None:
        print(
            "PyInstaller não encontrado. Instale-o no ambiente de build antes de empacotar.",
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryDirectory(prefix="ollama-configurator-pyinstaller-") as work_dir:
        subprocess.run(
            [
                pyinstaller,
                "--noconfirm",
                "--clean",
                "--onedir",
                "--name",
                "OllamaConfiguratorBackend",
                "--distpath",
                str(output),
                "--workpath",
                work_dir,
                "--specpath",
                work_dir,
                "--collect-submodules",
                "backend",
                str(ROOT / "backend" / "__main__.py"),
            ],
            cwd=ROOT,
            check=True,
        )

    print(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
