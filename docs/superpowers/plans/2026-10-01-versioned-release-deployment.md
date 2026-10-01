# Versioned Release and Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the next release (`0.1.9`) declare one application version consistently in development, the UI, backend health, package manifests, and macOS/Windows release artifacts.

**Architecture:** Add a repository-root `VERSION` file as the release source of truth. Runtime code reads that value in source builds and from the bundled resource in frozen builds; packaging scripts use the same value for manifests and platform metadata. The configurator exposes and displays its own version separately from the installed Ollama version.

**Tech Stack:** Python 3.12+, FastAPI, PyInstaller, React 18, Vite, npm lockfile, macOS plist, GitHub Actions.

## Global Constraints

- The next release version is `0.1.9`.
- `VERSION` is the only manually edited release-version file.
- `0.1.8` remains the current release until the release commit and tag are created.
- The Ollama runtime version and the Ollama Configurator application version must remain separate in API responses and UI copy.
- Release builds must remain local-only by default: API `127.0.0.1:8787`, gateway `11435`.
- No user model data or persisted configuration may be deleted or migrated as part of versioning.

---

### Task 1: Establish the single application-version source

**Files:**
- Create: `VERSION`
- Create: `backend/version.py`
- Modify: `backend/config.py`
- Modify: `scripts/build_backend.py`
- Modify: `scripts/build_frontend.mjs`
- Test: `tests/unit/test_version.py`
- Test: `tests/packaging/test_packaging_smoke.py`

**Interfaces:**
- `backend.version.get_version() -> str` returns the application version.
- `backend.version.read_version_file(path: Path) -> str` reads and validates one non-empty semantic version line.
- Both build scripts use `get_version()` or the shared file reader instead of independent `0.1.8` defaults.

- [ ] **Step 1: Write the failing version tests.**

```python
from pathlib import Path

from backend.version import read_version_file


def test_version_file_contains_the_next_release() -> None:
    assert read_version_file(Path("VERSION")) == "0.1.9"


def test_version_reader_rejects_blank_or_multiline_values(tmp_path: Path) -> None:
    invalid = tmp_path / "VERSION"
    invalid.write_text("\n0.1.9\n", encoding="utf-8")

    try:
        read_version_file(invalid)
    except ValueError as error:
        assert "version" in str(error).lower()
    else:
        raise AssertionError("invalid version file was accepted")
```

- [ ] **Step 2: Run the focused test and verify it fails because the shared reader does not exist.**

Run: `UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest tests/unit/test_version.py -q`

Expected: FAIL with an import or missing-file error for `backend.version`.

- [ ] **Step 3: Add `VERSION` with exactly `0.1.9` and implement the reader.**

```python
# backend/version.py
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
```

`VERSION` must contain:

```text
0.1.9
```

Update `backend/config.py` to set `version: str = get_version()`. Update both build scripts to use `get_version()` or the root `VERSION` file and remove `DEFAULT_VERSION = "0.1.8"`.

- [ ] **Step 4: Run the focused backend and packaging tests.**

Run: `UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest tests/unit/test_version.py tests/packaging/test_packaging_smoke.py -q`

Expected: all focused tests pass and both dry-run manifests report `0.1.9`.

- [ ] **Step 5: Commit the version-source change.**

```bash
git add VERSION backend/version.py backend/config.py scripts/build_backend.py scripts/build_frontend.mjs tests/unit/test_version.py tests/packaging/test_packaging_smoke.py
git commit -m "build: centralize application version"
```

### Task 2: Declare the version in the running application

**Files:**
- Modify: `backend/diagnostics/service.py`
- Modify: `backend/api/diagnostics_routes.py`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Modify: `frontend/src/features/shell/AppShell.tsx`
- Test: `tests/unit/test_health.py`
- Test: `tests/integration/test_diagnostics_routes.py`
- Test: `frontend/src/features/diagnostics/diagnostics.test.tsx`
- Test: `frontend/src/features/shell/appShell.test.tsx`

**Interfaces:**
- `GET /api/health` continues returning `{status, version}`.
- `GET /api/diagnostics` adds `application_version: string` while preserving the existing Ollama `ollama.version` field.
- `DiagnosticsSnapshot.application_version` is rendered as `Ollama Configurator v0.1.9` in the shell/footer or application status area.

- [ ] **Step 1: Add failing API/UI assertions for the application version.**

Backend assertion:

```python
def test_diagnostics_reports_configurator_version(client) -> None:
    response = client.get("/api/diagnostics")
    assert response.json()["application_version"] == "0.1.9"
```

Frontend assertion:

```tsx
expect(screen.getByText(/ollama configurator v0\.1\.9/i)).toBeInTheDocument();
```

- [ ] **Step 2: Run those tests and verify the new assertions fail.**

Run: `UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest tests/integration/test_diagnostics_routes.py -q` and `cd frontend && npm test -- --run src/features/diagnostics/diagnostics.test.tsx src/features/shell/appShell.test.tsx`.

Expected: existing diagnostics payloads lack `application_version` and the UI lacks the application-version label.

- [ ] **Step 3: Add the version field from `backend.version.get_version()` and render it in the shell.**

The frontend must use `application_version` for the configurator label and keep `ollama.version` for the Ollama runtime label. Do not replace one with the other.

- [ ] **Step 4: Run API, frontend, typecheck, and build checks.**

Run: `UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest tests/unit/test_health.py tests/integration/test_diagnostics_routes.py -q`, `cd frontend && npm test -- --run`, and `npm run build`.

Expected: all tests pass, the version label is visible, and the production build succeeds.

- [ ] **Step 5: Commit the application declaration change.**

```bash
git add backend/diagnostics/service.py backend/api/diagnostics_routes.py frontend/src/api/client.ts frontend/src/features/diagnostics/DiagnosticsPage.tsx frontend/src/features/shell/AppShell.tsx tests frontend/src/features/diagnostics/diagnostics.test.tsx frontend/src/features/shell/appShell.test.tsx
git commit -m "feat: show configurator application version"
```

### Task 3: Propagate the version into release artifacts

**Files:**
- Create: `packaging/macos/Info.plist.in`
- Modify: `packaging/macos/build-app.sh`
- Modify: `packaging/windows/build-installer.ps1`
- Modify: `tests/packaging/test_packaging_smoke.py`
- Modify: `docs/packaging.md`

**Interfaces:**
- macOS `CFBundleShortVersionString` and `CFBundleVersion` both equal `0.1.9`.
- Windows payload manifests equal `0.1.9`.
- Backend and frontend manifests produced by their builders equal `0.1.9`.

- [ ] **Step 1: Add failing artifact-version tests.**

```python
def test_macos_info_template_has_no_stale_release_version() -> None:
    template = (ROOT / "packaging/macos/Info.plist.in").read_text(encoding="utf-8")
    assert "@VERSION@" in template
    assert "0.1.8" not in template
```

- [ ] **Step 2: Run the packaging tests and verify the stale static plist is detected.**

Run: `UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest tests/packaging/test_packaging_smoke.py -q`.

Expected: FAIL until the static plist is replaced by a version-substituted template.

- [ ] **Step 3: Generate platform metadata from `VERSION`.**

Change `build-app.sh` to read the shared version and render `Info.plist.in` into the `.app` bundle before copying resources. Keep `Info.plist.in` free of `0.1.8` literals. Ensure the Windows script preserves the backend/frontend manifests generated with the shared version.

- [ ] **Step 4: Run dry-run and real staging checks where available.**

Run:

```bash
UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run python scripts/build_backend.py --dry-run
node scripts/build_frontend.mjs --dry-run
UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest tests/packaging/test_packaging_smoke.py -q
```

Expected: every manifest reports `0.1.9`, and no packaging source contains a stale `0.1.8` release declaration except historical documentation.

- [ ] **Step 5: Commit artifact propagation.**

```bash
git add packaging/macos/Info.plist.in packaging/macos/build-app.sh packaging/windows/build-installer.ps1 tests/packaging/test_packaging_smoke.py docs/packaging.md
git commit -m "build: propagate version into release artifacts"
```

### Task 4: Execute the release deployment checklist

**Files:**
- Modify: `docs/release-process.md`
- Modify: `docs/packaging.md`
- Test: `.github/workflows/test.yml`
- Release: Git tag `v0.1.9`

- [ ] **Step 1: Finish feature validation before changing the release version.**

Run:

```bash
UV_CACHE_DIR=/private/tmp/ollama-configurator-uv-cache uv run pytest -q
cd frontend && npm test -- --run && npm run typecheck && npm run build
```

Expected: backend and frontend suites pass, TypeScript passes, and the production build succeeds. Keep the gateway disabled during the model-profile test unless the gateway behavior is specifically being tested.

- [ ] **Step 2: Run local artifact dry-runs and verify version identity.**

Run the backend/frontend dry-runs and assert that `/api/health`, `/api/diagnostics`, both manifests, and the macOS plist all report `0.1.9`.

- [ ] **Step 3: Build native release artifacts.**

On macOS:

```bash
bash packaging/macos/build-app.sh
```

On Windows:

```powershell
powershell -ExecutionPolicy Bypass -File packaging/windows/build-installer.ps1
```

Expected: the macOS `.app`/`.dmg` and Windows `.zip` contain the same application version.

- [ ] **Step 4: Perform clean-machine smoke tests.**

For each platform, install the artifact, launch the configurator, verify the visible `Ollama Configurator v0.1.9` label and `GET /api/health`, test model selection plus `think` persistence for `qwen3.6`, and confirm that the user's Ollama models remain untouched after uninstall.

- [ ] **Step 5: Tag and publish only after clean-machine checks.**

```bash
git tag -a v0.1.9 -m "Release Ollama Configurator v0.1.9"
git push origin main v0.1.9
```

The tag triggers the native GitHub Actions workflows. Verify uploaded checksums and release assets before announcing the release.

- [ ] **Step 6: Commit the release documentation update.**

```bash
git add docs/release-process.md docs/packaging.md .github/workflows/test.yml
git commit -m "docs: document versioned release deployment"
```

## Self-Review

- The runtime version is sourced from `VERSION`, exposed through diagnostics, and shown separately from the Ollama runtime version.
- The backend/frontend manifests and macOS/Windows artifacts use the same value.
- Tests cover version parsing, API exposure, UI display, dry-run manifests, and release metadata.
- The deployment sequence preserves the existing model configuration and keeps the gateway's explicit network exposure separate from application versioning.

