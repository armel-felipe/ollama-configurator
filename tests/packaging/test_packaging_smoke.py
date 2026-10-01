from __future__ import annotations

import json
import plistlib
import subprocess
import sys
from pathlib import Path

from scripts.build_backend import _pyinstaller_command, _remove_macos_metadata

ROOT = Path(__file__).resolve().parents[2]


def _run(*args: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_backend_packaging_dry_run_is_local_and_versioned(tmp_path: Path) -> None:
    manifest = _run("scripts/build_backend.py", "--dry-run", "--output", str(tmp_path / "backend"))

    assert manifest["artifact"] == "OllamaConfiguratorBackend"
    assert manifest["bind_host"] == "127.0.0.1"
    assert manifest["ports"] == {"api": 8787, "gateway": 11435}
    assert manifest["version"] == "0.1.9"


def test_backend_packaging_uses_the_current_python_for_pyinstaller() -> None:
    assert _pyinstaller_command() == [sys.executable, "-m", "PyInstaller"]


def test_frontend_packaging_dry_run_is_versioned(tmp_path: Path) -> None:
    result = subprocess.run(
        ["node", "scripts/build_frontend.mjs", "--dry-run", "--output", str(tmp_path / "frontend")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest = json.loads(result.stdout)

    assert manifest["artifact"] == "OllamaConfiguratorFrontend"
    assert manifest["source"] == "frontend/dist"
    assert manifest["version"] == "0.1.9"


def test_frontend_package_excludes_macos_metadata(tmp_path: Path) -> None:
    output = tmp_path / "frontend"
    subprocess.run(
        ["node", "scripts/build_frontend.mjs", "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert not any(path.name.startswith("._") for path in output.rglob("*"))
    assert not any(path.name == ".DS_Store" for path in output.rglob("*"))


def test_backend_package_excludes_macos_metadata(tmp_path: Path) -> None:
    output = tmp_path / "backend"
    nested = output / "_internal" / "package.dist-info"
    nested.mkdir(parents=True)
    (nested / "._METADATA").write_text("metadata")
    (nested / ".DS_Store").write_text("finder")
    (nested / "METADATA").write_text("real metadata")

    _remove_macos_metadata(output)

    assert not any(path.name.startswith("._") for path in output.rglob("*"))
    assert not any(path.name == ".DS_Store" for path in output.rglob("*"))
    assert (nested / "METADATA").is_file()


def test_uninstall_dry_run_never_targets_ollama_models() -> None:
    manifest = _run("scripts/uninstall.py", "--dry-run")

    assert manifest["app_data_path"]
    assert "Ollama" not in str(manifest["preserved_paths"])
    assert any("models" in path for path in manifest["preserved_paths"])


def test_release_files_are_present() -> None:
    expected = [
        "backend/__main__.py",
        "packaging/macos/build-app.sh",
        "packaging/windows/build-installer.ps1",
        "packaging/windows/run.ps1",
        "docs/packaging.md",
        "docs/uninstall.md",
        "docs/release-process.md",
        ".github/workflows/test.yml",
        ".github/workflows/build-macos.yml",
        ".github/workflows/build-windows.yml",
    ]

    assert all((ROOT / path).exists() for path in expected)


def test_macos_bundle_declares_its_launcher_executable() -> None:
    with (ROOT / "packaging/macos/Info.plist").open("rb") as stream:
        info = plistlib.load(stream)

    assert info["CFBundleExecutable"] == "OllamaConfigurator"
