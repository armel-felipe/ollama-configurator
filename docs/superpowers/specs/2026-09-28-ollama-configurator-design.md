# Ollama Configurator — Technical Design

**Status:** Proposed
**Date:** 2026-09-28
**Source:** `PRD_ollama_configurator.md`

## Goal

Build a local-first, cross-platform application that lets users inspect and configure Ollama without manually editing files, Modelfiles, environment variables, or terminal commands.

## Product boundary

The source repository is a development project. The shipped product is a separately packaged macOS or Windows application that starts a local backend and opens a local web interface.

The application manages Ollama configuration and diagnostics, but does not replace Ollama, modify model weights, expose a remote administration service, or execute arbitrary shell commands.

## Recommended architecture

```text
React + Vite + TypeScript
            |
            | HTTP on 127.0.0.1
            v
FastAPI backend packaged with the application
            |
            +-- Ollama local API
            +-- hardware detection
            +-- persistent configuration store
            +-- macOS/Windows system adapters
```

During early development, the frontend is opened in the browser at the local backend URL. The backend is designed to be packaged as an application process later. A native desktop shell is not required for MVP 0.1.

## Core design decisions

1. Python is the backend language and FastAPI is the initial HTTP framework.
2. React/Vite/TypeScript is the frontend stack.
3. The default bind address is `127.0.0.1`; `0.0.0.0` is not used by default.
4. Model settings are persisted by the application and applied at runtime through explicit Ollama API operations.
5. `null` or an absent field means “Ollama Default”; it must not be replaced with `0`, `false`, or another arbitrary value.
6. Server settings are persisted through explicit OS adapters rather than temporary shell exports.
7. Configuration data is stored separately from installed program files.
8. Model weights are never deleted by configuration reset operations.
9. The initial supported systems are macOS and Windows. Linux is future scope.
10. Capabilities are derived from Ollama version, operating system, architecture, hardware, and supported settings; the UI does not assume every parameter exists everywhere.

## Dependency mapping requirement

Every dependency must be explicit, reproducible, and attributable to a project area.

### Runtime dependencies

- Backend Python packages: declared in `pyproject.toml` with version bounds.
- Frontend packages: declared in `frontend/package.json`.
- Ollama: treated as an external runtime dependency and checked by the diagnostics layer; its supported version range is documented rather than silently bundled.
- Packaged application runtime: documented for each target platform.

### Development dependencies

- Python test, lint, type-check, and formatting tools declared in a dedicated development dependency group.
- Frontend test, lint, type-check, and build tools declared in `frontend/package.json`.
- Node and Python minimum versions recorded in the repository documentation and CI configuration.

### Locking and reproducibility

- Commit `uv.lock` or the selected Python lockfile once the Python package manager is chosen.
- Commit `frontend/package-lock.json` or the selected npm-compatible lockfile.
- Do not mix package managers without documenting the reason.
- Record build commands and expected artifact names.
- CI must install from lockfiles and fail on undeclared dependencies.

### Platform and packaging dependencies

- macOS packaging tools and signing/notarization requirements documented separately from application runtime packages.
- Windows packaging tools and installer requirements documented separately from application runtime packages.
- Optional tools must be labeled as optional and must not be required for local development unless the current task needs packaging.

### Dependency documentation artifacts

The repository will include:

- `docs/dependencies.md`: inventory, purpose, ownership, compatibility, and upgrade policy.
- `docs/development-setup.md`: exact setup steps for macOS and Windows.
- `docs/packaging.md`: platform build prerequisites and artifact generation.
- `pyproject.toml`: backend metadata and Python dependencies.
- `uv.lock` or equivalent Python lockfile.
- `frontend/package.json`: frontend metadata and dependencies.
- `frontend/package-lock.json` or equivalent frontend lockfile.
- CI configuration that validates installation, tests, and builds from clean environments.

## Documentation set

```text
docs/
├── roadmap.md
├── architecture.md
├── dependencies.md
├── development-setup.md
├── api-contract.md
├── persistence.md
├── platform-adapters.md
├── security.md
├── testing.md
├── packaging.md
├── troubleshooting.md
├── runbooks/
└── decisions/
```

The documentation is versioned with the code. Each major architectural choice receives a short decision record explaining context, alternatives, and consequences.

## Incremental implementation roadmap

### Stage 0 — Repository and foundation

Create the source repository, project manifests, lockfiles, documentation structure, FastAPI health endpoint, frontend shell, local logging, and development commands.

**Exit gate:** a clean machine can install declared dependencies, start the backend and frontend, and pass the initial test suite.

### Stage 1 — Ollama and hardware discovery

Detect Ollama installation, version, API status, operating system, architecture, CPU, memory, GPU/backend where available, and installed models. Add the first useful read-only screen.

**Exit gate:** the user can see whether Ollama is usable and which models and hardware are available.

### Stage 2 — Basic model configuration

Implement supported basic model parameters, validation, runtime application through the Ollama API, persistent model overrides, and the explicit Default state.

**Exit gate:** a model configuration survives application restart without modifying model weights.

### Stage 3 — Model reset and safety behavior

Implement individual resets, global model reset, confirmations, missing-model state, and protection against deleting models or downloads.

**Exit gate:** every model override can be removed safely and predictably.

### Stage 4 — Persistent server configuration

Implement capability-aware server settings, the shared system adapter interface, macOS and Windows adapters, restart flow, permissions, and persistence across logout/login and reboot.

**Exit gate:** a supported server setting remains effective after Ollama and machine restart on both target systems.

### Stage 5 — MVP 0.1 integration

Integrate discovery, diagnostics, model settings, server settings, reset flows, restart, error handling, security checks, acceptance tests, and internal packaging validation.

**Exit gate:** a non-developer can install or start the application, use Ollama, change settings, and restore defaults without terminal commands.

### Stage 6 — MVP 0.2

Add advanced settings, profiles, explanations, contextual recommendations, benchmarks, and benchmark comparison.

### Stage 7 — MVP 0.3 distribution

Produce macOS and Windows installers, define uninstall/data-retention behavior, publish GitHub Releases, generate checksums, add advanced logs, import/export, and update checks.

## Security constraints

- Bind to `127.0.0.1` by default.
- Expose explicit operations only; never add a generic command execution endpoint.
- Validate model identifiers, paths, settings, and numeric ranges.
- Request only the permissions required by the active operation.
- Confirm global reset and restart operations.
- Keep program files and user data in separate platform-appropriate locations.

## Validation strategy

- Unit tests for configuration normalization, capability filtering, default semantics, and persistence.
- Integration tests against a controlled Ollama API boundary.
- Platform adapter tests for macOS and Windows behavior, with native validation on each platform.
- API contract tests for explicit endpoints and error responses.
- Frontend tests for loading, empty, missing, unsupported, and error states.
- Acceptance tests mapped directly to the PRD criteria.
- Clean-environment installation and build checks from lockfiles.

## Open decisions for the implementation plan

1. Select the Python package manager and lockfile format.
2. Select the Python packaging method for internal builds and final installers.
3. Define the persistence format and migration strategy.
4. Define the first supported Ollama version range and capability discovery method.
5. Define the exact macOS and Windows mechanisms for persistent server settings.

