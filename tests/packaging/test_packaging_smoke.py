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
    assert manifest["version"] == "0.1.18"


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
    assert manifest["version"] == "0.1.18"


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
        "packaging/posix/build-installer.sh",
        "packaging/posix/install.sh",
        "packaging/posix/run.sh",
        "packaging/posix/uninstall.sh",
        "packaging/windows/install.bat",
        "packaging/windows/run.bat",
        "packaging/windows/uninstall.bat",
        "packaging/windows/run.ps1",
        "docs/packaging.md",
        "docs/uninstall.md",
        "docs/release-process.md",
        ".github/workflows/test.yml",
        ".github/workflows/build-macos.yml",
        ".github/workflows/build-linux.yml",
        ".github/workflows/build-windows.yml",
    ]

    assert all((ROOT / path).exists() for path in expected)


def test_windows_batch_launchers_delegate_to_powershell_scripts() -> None:
    expected = {
        "install.bat": "install.ps1",
        "run.bat": "run.ps1",
        "uninstall.bat": "uninstall.ps1",
    }

    for batch_name, script_name in expected.items():
        content = (ROOT / "packaging/windows" / batch_name).read_text(encoding="utf-8")
        assert "powershell.exe" in content.lower()
        assert script_name in content
        assert "%~dp0" in content


def test_macos_bundle_declares_its_launcher_executable() -> None:
    with (ROOT / "packaging/macos/Info.plist").open("rb") as stream:
        info = plistlib.load(stream)

    assert info["CFBundleExecutable"] == "OllamaConfigurator"


def test_macos_launcher_opens_a_visible_server_terminal() -> None:
    launcher = (ROOT / "packaging/macos/OllamaConfigurator").read_text(encoding="utf-8")

    assert "tell application \"Terminal\"" in launcher
    assert "OLLAMA_CONFIGURATOR_TERMINAL_CHILD" in launcher
    assert "OLLAMA_CONFIGURATOR_OPEN_BROWSER=1" in launcher


def test_posix_release_scripts_are_shared_by_macos_and_linux() -> None:
    scripts = {
        "install.sh": "install",
        "run.sh": "run",
        "uninstall.sh": "uninstall",
    }

    for filename in scripts:
        content = (ROOT / "packaging/posix" / filename).read_text(encoding="utf-8")
        assert "Ollama Configurator" in content
        assert "#!/usr/bin/env bash" in content
        assert "uname -s" in content
    assert "SCRIPT_DIR=" in (ROOT / "packaging/posix/install.sh").read_text(encoding="utf-8")


def test_macos_installer_clears_download_quarantine_from_installed_bundle() -> None:
    content = (ROOT / "packaging/posix/install.sh").read_text(encoding="utf-8")

    assert 'uname -s' in content
    assert 'xattr -dr com.apple.quarantine "$INSTALL_DIR"' in content


def test_posix_builder_creates_zip_without_dmg_or_windows_launchers() -> None:
    content = (ROOT / "packaging/posix/build-installer.sh").read_text(encoding="utf-8")

    assert "OllamaConfigurator-" in content
    assert ".zip" in content
    assert "install.sh" in content
    assert "run.sh" in content
    assert "uninstall.sh" in content
    assert ".dmg" not in content
    assert ".bat" not in content
    assert "COPYFILE_DISABLE" in content


def test_release_workflows_keep_windows_and_publish_posix_zip_assets() -> None:
    macos_workflow = (ROOT / ".github/workflows/build-macos.yml").read_text(encoding="utf-8")
    linux_workflow = (ROOT / ".github/workflows/build-linux.yml").read_text(encoding="utf-8")
    windows_workflow = (ROOT / ".github/workflows/build-windows.yml").read_text(encoding="utf-8")

    assert "packaging/posix/build-installer.sh" in macos_workflow
    assert "OllamaConfigurator-macOS-arm64.zip" in macos_workflow
    assert ".dmg" not in macos_workflow
    assert "runs-on: ubuntu-latest" in linux_workflow
    assert "OllamaConfigurator-Linux-x86_64.zip" in linux_workflow
    assert "checksums-Linux.txt" in linux_workflow
    assert "install.bat" in windows_workflow
