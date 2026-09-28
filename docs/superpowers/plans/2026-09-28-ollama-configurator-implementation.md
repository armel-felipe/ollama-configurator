# Ollama Configurator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a locally installed macOS/Windows application that discovers Ollama and the host hardware, manages persistent model/server settings safely, and provides a local web UI without arbitrary shell execution.

**Architecture:** A FastAPI backend owns Ollama integration, capability filtering, persistence, diagnostics, and platform adapters. A React/Vite/TypeScript frontend consumes explicit localhost API endpoints. Development runs as separate processes; packaging later bundles the backend and built frontend into platform-specific installers.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic, httpx, pytest, Ruff, mypy; Node.js 22+, React, Vite, TypeScript, Vitest, Playwright; `uv` for Python dependencies; npm with `package-lock.json` for frontend dependencies; PyInstaller for application bundles; `create-dmg` for macOS disk images; Inno Setup for the Windows installer.

**Spec:** `docs/superpowers/specs/2026-09-28-ollama-configurator-design.md` and `PRD_ollama_configurator.md`

## Global Constraints

- Backend: **Python + FastAPI**.
- Interface: **web UI local**.
- Default bind address: **127.0.0.1**.
- Initial platforms: **macOS and Windows**.
- “Default” means **absence of override**; do not replace it with `0`, `false`, or another arbitrary value.
- Model configuration must not modify model weights.
- Reset operations must not remove models or Ollama downloads.
- No arbitrary shell endpoint such as `POST /run-command`.
- The UI must derive settings from **Ollama version + SO + hardware + capabilities**.
- Program files and user data must be stored separately.
- Dependencies must be declared, locked, documented, and installed from clean environments in CI.

## Review Focus

- Ollama unavailable, stopped, or returning malformed responses: the UI shows an actionable degraded state and never crashes.
- `Default` versus explicit falsy values (`0`, `false`, empty value): only Default removes an override.
- Model installed after startup or removed externally: refresh reconciles live models with saved configuration and marks missing models without deleting their settings.
- Unsupported settings on a given Ollama version/hardware: the API rejects them clearly and the UI does not offer them.
- Restart/reset failure or insufficient OS permission: configuration state is not falsely reported as applied, and recovery guidance is shown.

## Dependency and repository setup

### Task 1: Repository foundation and dependency manifests

**Files:**
- Create: `pyproject.toml`
- Create: `uv.lock`
- Create: `backend/app.py`
- Create: `backend/config.py`
- Create: `backend/logging_config.py`
- Create: `frontend/package.json`
- Create: `frontend/package-lock.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `tests/unit/test_health.py`
- Create: `frontend/src/App.test.tsx`
- Create: `README.md`
- Create: `docs/dependencies.md`
- Create: `docs/development-setup.md`
- Create: `docs/roadmap.md`
- Create: `.gitignore`

**Interfaces:**
- Produces `GET /api/health -> HealthResponse { status: "ok", version: string }`.
- Produces frontend command `npm run dev` and backend command `uv run uvicorn backend.app:app`.
- Produces dependency manifests and lockfiles for Python and frontend packages.

- [x] **Step 1: Write failing backend and frontend smoke tests**
- [x] **Step 2: Run the tests and verify they fail because the project is not scaffolded**
- [x] **Step 3: Add the manifests, minimal FastAPI app, Vite React shell, and typed health response**
- [x] **Step 4: Document runtime prerequisites, dependency ownership, lockfile policy, and setup commands**
- [x] **Step 5: Run `uv run pytest` and `npm test -- --run` and verify both pass**
- [x] **Step 6: Commit `chore: scaffold local application and dependency manifests`**

### Task 2: Shared domain models and configuration semantics

**Files:**
- Create: `backend/domain/models.py`
- Create: `backend/domain/settings.py`
- Create: `backend/domain/capabilities.py`
- Create: `backend/persistence/paths.py`
- Create: `backend/persistence/store.py`
- Create: `tests/unit/test_settings.py`
- Create: `tests/unit/test_capabilities.py`
- Create: `tests/unit/test_store.py`
- Modify: `docs/persistence.md`
- Modify: `docs/api-contract.md`

**Interfaces:**
- `ModelOverride(model: str, options: dict[str, JsonValue])`.
- `ServerOverride(options: dict[str, JsonValue])`.
- `PersistedConfig(models: dict[str, ModelOverride], server: ServerOverride)`.
- `normalize_options(options) -> dict[str, JsonValue]`: removes only values explicitly set to Default and preserves `0` and `false`.
- `ConfigStore.load() -> PersistedConfig` and `ConfigStore.save(config: PersistedConfig) -> None`.
- `filter_capabilities(capabilities, context) -> list[Capability]`.

- [x] **Step 1: Write tests for Default removal, explicit falsy values, atomic saves, missing files, and corrupted files**
- [x] **Step 2: Run `uv run pytest tests/unit/test_settings.py tests/unit/test_store.py -v` and verify failure**
- [x] **Step 3: Implement typed domain models, platform data paths, JSON persistence, schema versioning, and atomic replacement**
- [x] **Step 4: Add capability filtering tests for Apple/Metal, NVIDIA/CUDA/Vulkan, and AMD/ROCm/Vulkan contexts**
- [x] **Step 5: Run the focused unit tests and verify pass**
- [x] **Step 6: Commit `feat: add configuration domain and persistent store`**

### Task 3: Ollama client, discovery, and capabilities

**Files:**
- Create: `backend/ollama/client.py`
- Create: `backend/ollama/schemas.py`
- Create: `backend/ollama/discovery.py`
- Create: `backend/ollama/capabilities.py`
- Create: `backend/api/ollama_routes.py`
- Create: `tests/unit/test_ollama_client.py`
- Create: `tests/integration/test_ollama_routes.py`
- Modify: `backend/app.py`
- Modify: `docs/api-contract.md`

**Interfaces:**
- `OllamaClient(base_url: str, transport: Transport)`.
- `OllamaClient.get_version() -> OllamaVersion`.
- `OllamaClient.list_models() -> list[OllamaModel]`.
- `OllamaClient.generate(model: str, request: GenerateRequest) -> GenerateResult`.
- `discover_ollama() -> OllamaDiscovery`.
- `GET /api/ollama/status -> OllamaStatusResponse`.
- `GET /api/models -> ModelsResponse`.
- `GET /api/capabilities -> CapabilitiesResponse`.

- [x] **Step 1: Write mocked HTTP tests for successful discovery, timeout, connection refusal, malformed JSON, and empty model lists**
- [x] **Step 2: Run the focused tests and verify failure**
- [x] **Step 3: Implement the typed HTTP client with explicit timeouts and normalized errors**
- [x] **Step 4: Implement discovery and capability calculation without invoking a shell command endpoint**
- [x] **Step 5: Add routes and API error responses**
- [x] **Step 6: Run unit and integration tests and verify pass**
- [x] **Step 7: Commit `feat: add Ollama discovery and capability API`**

### Task 4: Hardware detection and read-only diagnostics UI

**Files:**
- Create: `backend/hardware/detector.py`
- Create: `backend/hardware/schemas.py`
- Create: `backend/diagnostics/service.py`
- Create: `backend/api/diagnostics_routes.py`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Create: `frontend/src/features/models/ModelsList.tsx`
- Create: `frontend/src/features/shared/StatusState.tsx`
- Create: `frontend/src/features/diagnostics/diagnostics.test.tsx`
- Create: `tests/unit/test_hardware_detector.py`
- Modify: `frontend/src/App.tsx`
- Modify: `docs/architecture.md`

**Interfaces:**
- `HardwareDetector.detect() -> HardwareSnapshot`.
- `GET /api/hardware -> HardwareSnapshot`.
- `GET /api/diagnostics -> DiagnosticsSnapshot`.
- Frontend `api.getDiagnostics(): Promise<DiagnosticsSnapshot>`.
- Frontend `api.getModels(): Promise<ModelsResponse>`.

- [x] **Step 1: Write detector tests using platform fixture providers, never the developer machine as the expected value**
- [x] **Step 2: Write frontend tests for loading, healthy, empty, missing-Ollama, and error states**
- [x] **Step 3: Run focused tests and verify failure**
- [x] **Step 4: Implement conservative hardware detection with unknown values when a signal is unavailable**
- [x] **Step 5: Implement diagnostics and the first usable read-only screen with refresh**
- [x] **Step 6: Run backend and frontend tests and perform a manual local smoke test**
- [x] **Step 7: Commit `feat: add local Ollama and hardware diagnostics screen`**

## MVP configuration implementation

### Task 5: Basic model settings and runtime application

**Files:**
- Create: `backend/ollama/options.py`
- Create: `backend/api/model_settings_routes.py`
- Create: `frontend/src/features/models/ModelSettingsPage.tsx`
- Create: `frontend/src/features/models/ParameterControl.tsx`
- Create: `frontend/src/features/models/modelSettings.test.tsx`
- Create: `tests/unit/test_model_options.py`
- Create: `tests/integration/test_model_settings_routes.py`
- Modify: `backend/ollama/client.py`
- Modify: `backend/app.py`
- Modify: `docs/api-contract.md`
- Modify: `docs/persistence.md`

**Interfaces:**
- `GET /api/models/{model_id}/settings -> ModelSettingsResponse`.
- `PUT /api/models/{model_id}/settings -> ModelSettingsResponse`.
- `POST /api/models/{model_id}/apply -> ApplyModelSettingsResponse`.
- `DELETE /api/models/{model_id}/settings/{parameter} -> ModelSettingsResponse`.
- `ModelSettingsService.get(model_id)`, `.update(model_id, patch)`, `.reset_parameter(model_id, parameter)`.

- [x] **Step 1: Write tests for basic parameters, range validation, unsupported parameters, model IDs containing tags, and Default semantics**
- [x] **Step 2: Run focused tests and verify failure**
- [x] **Step 3: Implement option schemas, capability-aware validation, persistence, and explicit runtime application**
- [x] **Step 4: Implement the model settings UI with Basic/Advanced separation reserved for later expansion**
- [x] **Step 5: Run tests and manually verify a setting survives application restart**
- [x] **Step 6: Commit `feat: add persistent basic model settings`**

### Task 6: Model reset flows and reconciliation

**Files:**
- Create: `backend/api/reset_routes.py`
- Create: `backend/persistence/reconciliation.py`
- Create: `frontend/src/features/settings/ResetControls.tsx`
- Create: `frontend/src/features/settings/resetControls.test.tsx`
- Create: `tests/unit/test_reconciliation.py`
- Create: `tests/integration/test_reset_routes.py`
- Modify: `backend/app.py`
- Modify: `docs/security.md`
- Modify: `docs/persistence.md`

**Interfaces:**
- `reconcile_saved_models(saved, installed) -> list[ModelState]`.
- `POST /api/reset/models -> ResetResult`.
- `POST /api/models/{model_id}/reset -> ResetResult`.
- `POST /api/models/{model_id}/settings/{parameter}/reset -> ResetResult`.

- [x] **Step 1: Write tests for global reset, individual reset, missing models, and proof that model files are not touched**
- [x] **Step 2: Run focused tests and verify failure**
- [x] **Step 3: Implement reconciliation and reset services using the ConfigStore only**
- [x] **Step 4: Add confirmation UI for global reset and clear result/error states**
- [x] **Step 5: Run tests and verify no Ollama model deletion API is called**
- [x] **Step 6: Commit `feat: add safe model reset and reconciliation`**

### Task 7: Effective model runtime profile and thinking controls

**Goal:** expose model-declared defaults and thinking controls, apply every saved runtime option by reloading the Ollama runner, and verify the effective context through `/api/ps`.

**Files:**
- Create: `backend/ollama/runtime.py`
- Create: `backend/api/model_runtime_routes.py`
- Create: `frontend/src/features/models/RuntimeStatus.tsx`
- Create: `frontend/src/features/models/runtimeStatus.test.tsx`
- Modify: `backend/ollama/client.py`
- Modify: `backend/ollama/options.py`
- Modify: `backend/ollama/schemas.py`
- Modify: `backend/api/model_settings_routes.py`
- Modify: `backend/app.py`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/models/ModelSettingsPage.tsx`
- Modify: `frontend/src/features/models/ParameterControl.tsx`
- Modify: `frontend/src/features/models/modelSettings.test.tsx`
- Create: `tests/unit/test_runtime_profile.py`
- Create: `tests/integration/test_model_runtime_routes.py`
- Modify: `tests/unit/test_ollama_client.py`
- Modify: `tests/integration/test_model_settings_routes.py`
- Modify: `docs/api-contract.md`
- Modify: `docs/persistence.md`

**Interfaces:**
- `OllamaClient.show_model(model_id) -> ModelSpec`.
- `OllamaClient.list_running_models() -> list[RunningModel]`.
- `OllamaClient.reload_model(model_id, options, think, keep_alive) -> None`.
- `GET /api/models/{model_id}/runtime -> RuntimeStatusResponse`.
- `GET /api/models/{model_id}/settings -> ModelSettingsResponse` including model-declared thinking values/default and native-default labels.
- `POST /api/models/{model_id}/apply -> ApplyModelSettingsResponse` including the applied profile and observed runtime status.
- Thinking values are accepted only when declared by `/api/show`; `false`, `true`, and model-defined strings are preserved exactly.
- Applying first unloads the current runner with `keep_alive=0`, then reloads it with the complete saved profile.
- Context presets are 16K/32K/64K/128K/256K and custom positive integer input remains available.

- [x] **Step 1: Write failing tests for `/api/show`, `/api/ps`, model-defined thinking values/defaults, runner reload, and effective runtime status.**
- [x] **Step 2: Run focused backend/frontend tests and verify the expected failures.**
- [x] **Step 3: Implement typed Ollama model-spec/runtime client methods and strict thinking validation.**
- [x] **Step 4: Implement apply-as-unload-then-reload and runtime status routes; retain the last applied profile for fields Ollama does not expose in `/api/ps`.**
- [x] **Step 5: Implement presets, free input, thinking controls, native-default labels, dirty/saved/applied states, and runtime status UI.**
- [x] **Step 6: Run focused tests, then the complete project gauntlet and manual browser QA against the local Ollama models.**
- [x] **Step 7: Commit `feat: add verified model runtime profiles and thinking controls`.**

### Task 7A: Inference verification panel and thinking enforcement

**Status:** Blocking gate before Task 8.

**Goal:** prove the behavior of the saved model profile through an inference
request originated by the application, rather than inferring it only from
saved state or runner metadata.

**Files:**
- Create: `backend/api/inference_routes.py`
- Create: `backend/inference/service.py`
- Create: `frontend/src/features/models/InferenceTestPanel.tsx`
- Create: `frontend/src/features/models/inferenceTest.test.tsx`
- Create: `tests/unit/test_inference_service.py`
- Create: `tests/integration/test_inference_routes.py`
- Modify: `backend/ollama/client.py`
- Modify: `backend/app.py`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Modify: `docs/api-contract.md`
- Modify: `docs/persistence.md`

**Interfaces:**
- `POST /api/models/{model_id}/inference-test` accepts `{ "prompt": string }` and returns the requested profile, final response, optional thinking output, and runtime status.
- `InferenceService.run(model_id, prompt) -> InferenceResult` loads the persisted model profile and sends `think` as a top-level Ollama request field.
- The UI displays `Thinking solicitado`, `Thinking recebido`, `Contexto efetivo`, and the final response separately.
- `think=false` is verified by absence of a non-empty `thinking` field and absence of leaked `<think>` tags in the final response.
- `think=true` or a supported named level is verified by the model response when the model emits thinking.
- The application does not claim to control an unrelated interactive `ollama run` session; that limitation is visible in the UI.

- [x] **Step 1: Write failing tests for inference with `think=false`, `think=true`, named levels, profile merging, and leaked thinking tags.**
- [x] **Step 2: Run focused backend/frontend tests and verify the expected failures.**
- [x] **Step 3: Implement the inference service and route using the saved profile on every request.**
- [x] **Step 4: Implement the panel with separate thinking/final response, requested/observed state, loading, error, and limitation messaging.**
- [x] **Step 5: Run the exact Gemma4 prompt test and verify `think=false` produces no thinking output.**
- [x] **Step 6: Run the complete project gauntlet and manual browser QA.**
- [x] **Step 7: Mark Task 7A complete only after the inference acceptance gate passes.**
- [x] **Step 8: Commit `feat: add verified in-app inference testing`.**

### Task 7B: Managed runtime gateway for Ollama and OpenAI clients

**Status:** Complete.

**Goal:** make the saved profile effective for OpenCode and other clients by
providing one managed local entry point that injects model settings before
forwarding requests to Ollama.

**Files:**
- Create: `backend/gateway.py`
- Create: `backend/gateway_service.py`
- Create: `tests/unit/test_gateway_service.py`
- Create: `tests/integration/test_gateway_routes.py`
- Modify: `backend/ollama/client.py`
- Modify: `docs/api-contract.md`
- Modify: `docs/development-setup.md`
- Modify: `README.md`
- Modify: `docs/security.md`

**Interfaces:**
- `POST /api/generate` on the gateway forwards to Ollama with the saved profile merged into the request.
- `POST /v1/chat/completions` accepts the OpenAI chat shape and forwards it using the saved model profile.
- `GET /api/tags`, `GET /api/version`, `POST /api/show`, and `GET /api/ps` provide compatibility/diagnostic pass-throughs.
- Default listener is `127.0.0.1:11435`; Tailscale exposure requires an explicit bind address and `OLLAMA_GATEWAY_API_KEY`.
- Explicit saved values override client-provided values; Default means the client/Ollama default remains available.
- Streaming is rejected clearly until a token-streaming adapter is implemented; non-streaming requests are supported and verified.

- [x] **Step 1: Write failing tests for profile injection, Default semantics, Ollama-compatible generate, OpenAI-compatible chat, and API-key protection.**
- [x] **Step 2: Run focused tests and verify the expected failures.**
- [x] **Step 3: Implement the gateway service and Ollama/OpenAI routes.**
- [x] **Step 4: Add local default binding, explicit Tailscale binding guidance, and API-key enforcement.**
- [x] **Step 5: Run the complete project gauntlet and manual OpenCode-compatible HTTP QA.**
- [x] **Step 6: Mark Task 7B complete and commit `feat: add managed runtime gateway`.**

### Task 7C: Streaming adapter for Ollama and OpenAI clients

**Status:** Complete.

**Goal:** support real incremental responses through the managed gateway so
OpenCode can render model output while it is generated, without losing the
saved profile or the distinction between thinking and final content.

**Files:**
- Create: `tests/integration/test_gateway_streaming.py`
- Modify: `backend/ollama/client.py`
- Modify: `backend/gateway_service.py`
- Modify: `backend/gateway.py`
- Modify: `tests/unit/test_gateway_service.py`
- Modify: `docs/api-contract.md`
- Modify: `docs/security.md`

**Interfaces:**
- `POST /api/generate` with `stream=true` returns Ollama NDJSON chunks.
- `POST /v1/chat/completions` with `stream=true` returns OpenAI SSE chunks and a final `[DONE]` marker.
- Saved explicit values still override client values in streaming requests.
- `think=false` is forwarded on the initial Ollama request and no thinking delta is emitted.
- Connection failures and mid-stream failures terminate with an explicit error event/log.

- [x] **Step 1: Write failing tests for Ollama NDJSON streaming, OpenAI SSE conversion, profile injection, `think=false`, and `[DONE]`.**
- [x] **Step 2: Run focused tests and verify the expected failures.**
- [x] **Step 3: Implement streaming methods in the Ollama client and gateway service.**
- [x] **Step 4: Implement NDJSON/SSE HTTP responses and stream error handling.**
- [x] **Step 5: Run the complete project gauntlet and test the real Gemma4 through the gateway.**
- [x] **Step 6: Verify OpenCode-compatible streaming and commit `feat: enable gateway streaming`.**

### Task 7D: Native Ollama chat compatibility

**Status:** Complete.

**Goal:** make `OLLAMA_HOST=http://host:11435 ollama run model` pass through
the managed profile by implementing the native `/api/chat` contract.

**Files:**
- Create: `tests/integration/test_gateway_ollama_chat.py`
- Modify: `backend/gateway_service.py`
- Modify: `backend/gateway.py`
- Modify: `docs/api-contract.md`
- Modify: `docs/development-setup.md`

**Interfaces:**
- `POST /api/chat` returns the native Ollama chat response for `stream=false`.
- `POST /api/chat` returns native Ollama NDJSON chunks for `stream=true`.
- Saved model settings are injected into both modes, including `think=false`.
- `OLLAMA_HOST` can point Ollama CLI and compatible clients to the gateway port.

- [x] **Step 1: Write failing tests for native chat response, native chat streaming, and saved profile injection.**
- [x] **Step 2: Run focused tests and verify the expected failures.**
- [x] **Step 3: Implement the native chat route and profile-aware service methods.**
- [x] **Step 4: Run the complete project gauntlet and test through `OLLAMA_HOST`.**
- [x] **Step 5: Mark Task 7D complete and commit `feat: support native Ollama chat gateway`.**

### Task 8: Server settings abstraction and macOS adapter

**PRD coverage:** Sections 15–20. Server settings are global, visible before
model selection, persistent across Ollama close/logout/login/reboot, and are
applied through one restart/reconciliation path regardless of whether the
request originated in the server screen, model screen, startup bootstrap, or
an explicit restart action.

**Files:**
- Create: `backend/os_adapters/base.py`
- Create: `backend/os_adapters/macos.py`
- Create: `backend/server_settings/catalog.py`
- Create: `backend/server_settings/service.py`
- Create: `backend/server_settings/restart_coordinator.py`
- Create: `backend/api/server_settings_routes.py`
- Create: `frontend/src/features/server/ServerSettingsPage.tsx`
- Create: `frontend/src/features/server/serverSettings.test.tsx`
- Create: `tests/unit/test_server_settings.py`
- Create: `tests/unit/test_macos_adapter.py`
- Create: `tests/integration/test_server_settings_routes.py`
- Modify: `backend/app.py`
- Modify: `docs/platform-adapters.md`

**Interfaces:**
- `SystemAdapter.get_environment(name: str) -> str | None`.
- `SystemAdapter.set_environment(name: str, value: str) -> None`.
- `SystemAdapter.remove_environment(name: str) -> None`.
- `SystemAdapter.restart_ollama() -> RestartResult`.
- `SystemAdapter.open_logs() -> None`.
- `ServerSettingsService.get()`, `.update(patch)`, `.reset()`, `.restart()`.
- `RestartCoordinator.restart_and_reapply_profiles() -> RestartResult`.
- Server catalog includes `OLLAMA_KV_CACHE_TYPE`, `OLLAMA_FLASH_ATTENTION`, `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_KEEP_ALIVE`, `OLLAMA_NUM_PARALLEL`, `OLLAMA_MAX_LOADED_MODELS`, `OLLAMA_MAX_QUEUE`, `OLLAMA_GPU_OVERHEAD`, scheduler and integrated-GPU settings when supported.
- `OLLAMA_KV_CACHE_TYPE` is global; the UI exposes its effective value before model configuration, marks changes as restart-pending, restarts Ollama, reapplies saved model profiles, and verifies the post-restart state.
- `GET /api/server/settings`.
- `PUT /api/server/settings`.
- `POST /api/server/settings/reset`.
- `POST /api/server/restart`.
- `GET /api/server/runtime` returns server settings, restart-pending state, API availability, and model reapplication results.

- [ ] **Step 1: Write adapter contract tests with a fake process/environment boundary**
- [ ] **Step 2: Write macOS persistence tests for install, update, remove, restart, and permission failure**
- [ ] **Step 3: Run focused tests and verify failure**
- [ ] **Step 4: Implement the shared adapter contract and macOS persistence with a managed per-user LaunchAgent that reapplies configured environment values at login and a controlled Ollama restart; reset removes the managed LaunchAgent and its overrides**
- [ ] **Step 5: Implement capability-aware server setting validation, including KV cache values supported by the installed Ollama, and explicit reset-as-removal**
- [ ] **Step 6: Implement `RestartCoordinator` so every restart path reapplies server settings first, then saved model profiles, then verifies runtime; no caller may invoke a raw restart independently**
- [ ] **Step 7: Add server UI controls visible before model selection, restart confirmation, pending/applied/error states, and post-restart diagnostics**
- [ ] **Step 8: Validate KV cache, global context, Flash Attention, persistence across Ollama restart/logout/login/reboot, and model-profile reapplication on macOS**
- [ ] **Step 9: Commit `feat: add persistent macOS server settings`**

### Task 9: Windows adapter and cross-platform server settings

**Files:**
- Create: `backend/os_adapters/windows.py`
- Create: `tests/unit/test_windows_adapter.py`
- Create: `tests/integration/test_windows_server_persistence.py`
- Modify: `backend/os_adapters/base.py`
- Modify: `backend/server_settings/service.py`
- Modify: `docs/platform-adapters.md`
- Modify: `docs/development-setup.md`

**Interfaces:**
- Implements the same `SystemAdapter` interface as Task 7.
- No Windows-specific behavior may leak into API route contracts.

- [ ] **Step 1: Write Windows adapter tests for persistent user settings, removal, restart, and permission failure**
- [ ] **Step 2: Run cross-platform unit tests and verify failure on the unimplemented adapter**
- [ ] **Step 3: Implement the Windows adapter using the selected persistent user/system mechanism**
- [ ] **Step 4: Run native Windows validation for logout/login and reboot persistence**
- [ ] **Step 5: Commit `feat: add persistent Windows server settings`**

## MVP integration and distribution

### Task 10: MVP 0.1 diagnostics, security, and acceptance suite

**Files:**
- Create: `tests/acceptance/test_mvp_01.py`
- Create: `tests/security/test_local_only.py`
- Create: `docs/testing.md`
- Create: `docs/runbooks/ollama-unavailable.md`
- Modify: `backend/app.py`
- Modify: `frontend/src/App.tsx`
- Modify: `README.md`

- [ ] **Step 1: Map each PRD acceptance criterion to a test or documented native validation**
- [ ] **Step 2: Add tests proving localhost binding and absence of arbitrary command routes**
- [ ] **Step 3: Add end-to-end flows for discovery, model settings, server settings, restart, and reset**
- [ ] **Step 4: Run backend, frontend, security, and acceptance suites from clean lockfile installs**
- [ ] **Step 5: Validate the complete flow on macOS and Windows**
- [ ] **Step 6: Commit `test: validate MVP 0.1 acceptance criteria`**

### Task 11: Packaging, installers, and release documentation

**Files:**
- Create: `packaging/macos/`
- Create: `packaging/windows/`
- Create: `scripts/build_backend.py`
- Create: `scripts/build_frontend.mjs`
- Create: `docs/packaging.md`
- Create: `docs/uninstall.md`
- Create: `docs/release-process.md`
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/build-macos.yml`
- Create: `.github/workflows/build-windows.yml`

- [ ] **Step 1: Write packaging smoke tests for artifact existence, version reporting, localhost binding, and clean uninstall behavior**
- [ ] **Step 2: Build the backend with PyInstaller and the frontend from its lockfile**
- [ ] **Step 3: Create macOS `.app`/`.dmg` and Windows installer artifacts**
- [ ] **Step 4: Document data retention, uninstall behavior, signing, notarization, checksums, and GitHub Releases**
- [ ] **Step 5: Run clean-machine installation, launch, upgrade, and uninstall validation on both platforms**
- [ ] **Step 6: Commit `build: add cross-platform packaging pipeline`**

## Later plan boundary

MVP 0.2 gets a separate plan after MVP 0.1 is validated. It will cover advanced settings, profiles, recommendations, benchmark execution, metric collection, and comparisons. MVP 0.3 packaging work may be split into a separate release plan if installer validation exposes platform-specific complexity.

## Execution handoff

Implement this plan in order. Use `superpowers:executing-plans` for native implementation or `superpowers:subagent-driven-development` for task-by-task delegated implementation. Do not begin implementation until the repository location and Git initialization/clone target are confirmed.
