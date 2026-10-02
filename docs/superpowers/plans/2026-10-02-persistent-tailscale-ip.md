# Persistent Tailscale Connection IP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `<IP_TAILSCALE>` connection placeholder with a user-entered, backend-persisted IP used by macOS/Linux and Windows commands.

**Architecture:** Extend `GatewaySettingsService` so the existing `gateway` configuration owns an optional `tailscale_ip` independently from the bind host. Expose a dedicated write endpoint, inject the client functions into `ConnectionsPage`, and treat the persisted value—not an unsaved draft—as the only source for generated commands.

**Tech Stack:** Python 3.13, FastAPI, Pydantic, stdlib `ipaddress`, React 19, TypeScript, Vitest, Testing Library, pytest/httpx.

## Global Constraints

- Accept IP addresses only; reject DNS and MagicDNS names.
- Accept valid IPv4 and IPv6 and bracket IPv6 when building an HTTP URL.
- Persist in the backend `config.json`, not browser storage.
- Saving the bind must preserve `tailscale_ip`; saving `tailscale_ip` must preserve the bind.
- Local mode always uses `127.0.0.1`; network mode requires a persisted IP and never copies `<IP_TAILSCALE>`.
- macOS/Linux uses `export OLLAMA_HOST=...`; Windows PowerShell uses `$env:OLLAMA_HOST="..."`.
- Saving the client IP must not restart the gateway or execute Tailscale.
- Do not add dependencies.

---

## File Structure

- `backend/gateway_settings.py`: validate, normalize, read, and persist the optional client IP alongside gateway bind state.
- `backend/api/gateway_routes.py`: expose the dedicated `PUT /api/gateway/tailscale-ip` operation.
- `frontend/src/api/client.ts`: model `tailscale_ip` and call the dedicated endpoint.
- `frontend/src/features/connections/connectionCommands.ts`: format the persisted IP as a gateway URL, including IPv6 brackets.
- `frontend/src/features/connections/ConnectionsPage.tsx`: load, edit, save, and consume the persisted IP.
- `frontend/src/features/diagnostics/DiagnosticsPage.tsx`: inject the gateway settings API into `ConnectionsPage`.
- `frontend/src/styles/app.css`: style the inline IP editor and its success/error states.
- Existing backend and frontend test files remain responsible for their corresponding units; no new abstraction file is needed.

---

### Task 1: Persist and validate the Tailscale client IP

**Files:**
- Modify: `backend/gateway_settings.py`
- Test: `tests/unit/test_gateway_settings.py`

**Interfaces:**
- Consumes: existing `ConfigStore.load() -> dict[str, Any]` and `ConfigStore.save(config) -> None`.
- Produces: `validate_tailscale_ip(value: str) -> str`, `GatewaySettingsState.tailscale_ip: str | None`, and `GatewaySettingsService.update_tailscale_ip(value: str, effective_host: str) -> GatewaySettingsState`.

- [ ] **Step 1: Write failing service tests**

Add tests covering canonical persistence, independent field preservation, validation, IPv6, and reset:

```python
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("100.87.71.48", "100.87.71.48"),
        (" fd7a:115c:a1e0::1 ", "fd7a:115c:a1e0::1"),
    ],
)
def test_tailscale_ip_is_validated_normalized_and_persisted(
    tmp_path: Path, value: str, expected: str
) -> None:
    gateway_service = service(tmp_path)
    gateway_service.update("0.0.0.0", effective_host=DEFAULT_GATEWAY_HOST)

    state = gateway_service.update_tailscale_ip(value, effective_host=DEFAULT_GATEWAY_HOST)

    assert state.tailscale_ip == expected
    assert state.host == "0.0.0.0"
    assert ConfigStore(tmp_path / "config.json").load()["gateway"] == {
        "host": "0.0.0.0",
        "tailscale_ip": expected,
    }


@pytest.mark.parametrize("value", ["", "mac.tailnet.ts.net", "http://100.87.71.48", "100.87.71.48:11435"])
def test_invalid_tailscale_ip_is_rejected_without_overwriting_saved_value(
    tmp_path: Path, value: str
) -> None:
    gateway_service = service(tmp_path)
    gateway_service.update_tailscale_ip("100.64.0.10", effective_host=DEFAULT_GATEWAY_HOST)

    with pytest.raises(ValueError, match="IP Tailscale"):
        gateway_service.update_tailscale_ip(value, effective_host=DEFAULT_GATEWAY_HOST)

    assert gateway_service.get(DEFAULT_GATEWAY_HOST).tailscale_ip == "100.64.0.10"


def test_updating_bind_preserves_saved_tailscale_ip(tmp_path: Path) -> None:
    gateway_service = service(tmp_path)
    gateway_service.update_tailscale_ip("100.64.0.10", effective_host=DEFAULT_GATEWAY_HOST)

    state = gateway_service.update("0.0.0.0", effective_host=DEFAULT_GATEWAY_HOST)

    assert state.tailscale_ip == "100.64.0.10"
```

Extend the reset assertion so `state.tailscale_ip is None` and the removed `gateway` section proves both fields reset together.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `uv run pytest tests/unit/test_gateway_settings.py -q`

Expected: FAIL because `tailscale_ip` and `update_tailscale_ip` do not exist.

- [ ] **Step 3: Implement validation and independent persistence**

Use `ipaddress.ip_address` as the authoritative validator:

```python
from ipaddress import ip_address


def validate_tailscale_ip(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Informe um IP Tailscale válido")
    try:
        return str(ip_address(normalized))
    except ValueError as error:
        raise ValueError("Informe um IP Tailscale válido, sem protocolo ou porta") from error
```

Add `tailscale_ip: str | None = None` to `GatewaySettingsState` and its serialized dictionary. In `get`, validate a saved string or return `None`. In `update`, merge the existing gateway dictionary before replacing `host`. Add:

```python
def update_tailscale_ip(self, value: str, effective_host: str) -> GatewaySettingsState:
    tailscale_ip = validate_tailscale_ip(value)
    effective = validate_gateway_host(effective_host)
    config = self.store.load()
    saved_gateway = config.get("gateway", {})
    gateway = dict(saved_gateway) if isinstance(saved_gateway, dict) else {}
    host = validate_gateway_host(gateway.get("host", DEFAULT_GATEWAY_HOST))
    gateway["host"] = host
    gateway["tailscale_ip"] = tailscale_ip
    config["gateway"] = gateway
    self.store.save(config)
    LOG_STORE.emit("configurator", "info", "IP Tailscale salvo", {"tailscale_ip": tailscale_ip})
    return self._state(host, effective, tailscale_ip)
```

Update `_state` calls and signature so every state carries the saved IP.

- [ ] **Step 4: Run service tests and confirm GREEN**

Run: `uv run pytest tests/unit/test_gateway_settings.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit the service unit**

```bash
git add backend/gateway_settings.py tests/unit/test_gateway_settings.py
git commit -m "feat: persist Tailscale connection IP"
```

---

### Task 2: Expose the dedicated API contract

**Files:**
- Modify: `backend/api/gateway_routes.py`
- Modify: `frontend/src/api/client.ts`
- Test: `tests/integration/test_gateway_settings_routes.py`
- Test: `frontend/src/api/client.test.ts`

**Interfaces:**
- Consumes: `GatewaySettingsService.update_tailscale_ip(value, effective_host)` from Task 1.
- Produces: `PUT /api/gateway/tailscale-ip`, `GatewaySettings.tailscale_ip`, and `saveGatewayTailscaleIp(tailscaleIp: string): Promise<GatewaySettings>`.

- [ ] **Step 1: Write failing route tests**

Add integration coverage:

```python
@pytest.mark.asyncio
async def test_gateway_tailscale_ip_endpoint_persists_without_restarting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    manager = FakeSettingsManager()
    async with await client_for(monkeypatch, tmp_path, manager) as client:
        response = await client.put(
            "/api/gateway/tailscale-ip", json={"tailscale_ip": "100.87.71.48"}
        )

    assert response.status_code == 200
    assert response.json()["tailscale_ip"] == "100.87.71.48"
    assert manager.restart_hosts == []
    assert ConfigStore(tmp_path / "config.json").load()["gateway"]["tailscale_ip"] == "100.87.71.48"


@pytest.mark.asyncio
async def test_gateway_tailscale_ip_endpoint_rejects_hostname(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    async with await client_for(monkeypatch, tmp_path, FakeSettingsManager()) as client:
        response = await client.put(
            "/api/gateway/tailscale-ip", json={"tailscale_ip": "mac.tailnet.ts.net"}
        )

    assert response.status_code == 422
    assert "IP Tailscale" in response.json()["detail"]
```

- [ ] **Step 2: Run route tests and confirm RED**

Run: `uv run pytest tests/integration/test_gateway_settings_routes.py -q`

Expected: new endpoint tests fail with `404`.

- [ ] **Step 3: Add the FastAPI route**

Define the request and route without restarting the manager:

```python
class GatewayTailscaleIpUpdate(BaseModel):
    tailscale_ip: str


@router.put("/tailscale-ip")
def update_gateway_tailscale_ip(patch: GatewayTailscaleIpUpdate) -> dict[str, object]:
    manager = get_gateway_manager()
    try:
        return _settings_service().update_tailscale_ip(
            patch.tailscale_ip,
            effective_host=manager.host,
        ).to_dict()
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
```

- [ ] **Step 4: Add failing frontend client tests**

In `frontend/src/api/client.test.ts`, mock `fetch` and assert:

```typescript
it("persists the Tailscale client IP", async () => {
  const response = { host: "0.0.0.0", effective_host: "0.0.0.0", port: 11435, pending_restart: false, options: [], tailscale_ip: "100.87.71.48" };
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify(response), { status: 200 }));

  await expect(saveGatewayTailscaleIp("100.87.71.48")).resolves.toEqual(response);
  expect(fetch).toHaveBeenCalledWith("/api/gateway/tailscale-ip", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailscale_ip: "100.87.71.48" }),
  });
});
```

- [ ] **Step 5: Implement the TypeScript client contract**

Add `tailscale_ip?: string | null` to `GatewaySettings` and:

```typescript
export async function saveGatewayTailscaleIp(tailscaleIp: string): Promise<GatewaySettings> {
  const response = await fetch("/api/gateway/tailscale-ip", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailscale_ip: tailscaleIp }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Não foi possível salvar o IP Tailscale");
  }
  return response.json() as Promise<GatewaySettings>;
}
```

- [ ] **Step 6: Run API and client tests**

Run: `uv run pytest tests/integration/test_gateway_settings_routes.py -q`

Run: `npm test --prefix frontend -- --run src/api/client.test.ts`

Expected: both commands pass.

- [ ] **Step 7: Commit the API contract**

```bash
git add backend/api/gateway_routes.py frontend/src/api/client.ts tests/integration/test_gateway_settings_routes.py frontend/src/api/client.test.ts
git commit -m "feat: expose Tailscale IP settings API"
```

---

### Task 3: Generate URLs from persisted IPs

**Files:**
- Modify: `frontend/src/features/connections/connectionCommands.ts`
- Test: `frontend/src/features/connections/connectionCommands.test.ts`

**Interfaces:**
- Produces: `gatewayUrlForIp(ip: string, port: number): string`.
- Consumed by: `ConnectionsPage` in Task 4.

- [ ] **Step 1: Write failing formatter tests**

```typescript
describe("gatewayUrlForIp", () => {
  it("formats IPv4 without brackets", () => {
    expect(gatewayUrlForIp("100.87.71.48", 11435)).toBe("http://100.87.71.48:11435");
  });

  it("brackets IPv6 for an HTTP URL", () => {
    expect(gatewayUrlForIp("fd7a:115c:a1e0::1", 11435)).toBe("http://[fd7a:115c:a1e0::1]:11435");
  });
});
```

- [ ] **Step 2: Run the formatter test and confirm RED**

Run: `npm test --prefix frontend -- --run src/features/connections/connectionCommands.test.ts`

Expected: FAIL because `gatewayUrlForIp` is not exported.

- [ ] **Step 3: Implement the focused formatter**

```typescript
export function gatewayUrlForIp(ip: string, port: number): string {
  const host = ip.includes(":") ? `[${ip}]` : ip;
  return `http://${host}:${port}`;
}
```

- [ ] **Step 4: Run formatter tests and commit**

Run: `npm test --prefix frontend -- --run src/features/connections/connectionCommands.test.ts`

Expected: all focused tests pass.

```bash
git add frontend/src/features/connections/connectionCommands.ts frontend/src/features/connections/connectionCommands.test.ts
git commit -m "feat: format persisted gateway client IP"
```

---

### Task 4: Add the persistent IP editor to Connections

**Files:**
- Modify: `frontend/src/features/connections/ConnectionsPage.tsx`
- Modify: `frontend/src/features/connections/connections.test.tsx`
- Modify: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Modify: `frontend/src/styles/app.css`

**Interfaces:**
- Consumes: `getGatewaySettings(): Promise<GatewaySettings>`, `saveGatewayTailscaleIp(ip): Promise<GatewaySettings>`, and `gatewayUrlForIp(ip, port)`.
- Produces: a controlled editor whose copied commands use only `savedTailscaleIp`.

- [ ] **Step 1: Write failing component tests for loading and platform commands**

Extend the page props with injected `loadGatewaySettings` and `saveTailscaleIp`. Replace the placeholder test with:

```typescript
it("loads the persisted IP and uses it for macOS and Windows commands", async () => {
  const writeText = vi.fn().mockResolvedValue(undefined);
  Object.assign(navigator, { clipboard: { writeText } });
  const settings = { host: "0.0.0.0", effective_host: "0.0.0.0", port: 11435, pending_restart: false, options: [], tailscale_ip: "100.87.71.48" };
  render(<ConnectionsPage
    models={models}
    selectedModel={models[0].name}
    gateway={{ state: "running", host: "0.0.0.0", port: 11435 }}
    onSelectModel={() => undefined}
    loadGatewaySettings={vi.fn().mockResolvedValue(settings)}
    saveTailscaleIp={vi.fn()}
  />);

  expect(await screen.findByLabelText(/IP Tailscale da máquina servidora/i)).toHaveValue("100.87.71.48");
  fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
  await waitFor(() => expect(writeText).toHaveBeenLastCalledWith("export OLLAMA_HOST=http://100.87.71.48:11435\nollama run qwen3.8:27b-mlx --verbose"));

  fireEvent.change(screen.getByLabelText(/shell/i), { target: { value: "powershell" } });
  fireEvent.click(screen.getByRole("button", { name: /^terminal executar/i }));
  await waitFor(() => expect(writeText).toHaveBeenLastCalledWith('$env:OLLAMA_HOST="http://100.87.71.48:11435"\nollama run qwen3.8:27b-mlx --verbose'));
});
```

- [ ] **Step 2: Write failing save and blocked-copy tests**

Add one test that types `100.64.0.22`, clicks **Salvar IP**, verifies the API call and success text, and then verifies the next copied command uses that saved response. Add another where `tailscale_ip` is `null`, click a card, assert `writeText` was not called, and assert **Informe e salve o IP Tailscale antes de copiar o comando.** appears.

- [ ] **Step 3: Run component tests and confirm RED**

Run: `npm test --prefix frontend -- --run src/features/connections/connections.test.tsx`

Expected: FAIL because the editor props and UI do not exist.

- [ ] **Step 4: Implement loading, explicit save, and copy guard**

Add props:

```typescript
loadGatewaySettings: () => Promise<GatewaySettings>;
saveTailscaleIp: (ip: string) => Promise<GatewaySettings>;
```

Add `draftTailscaleIp`, `savedTailscaleIp`, `tailscaleStatus`, `tailscaleError`, and an input ref. Load once with `useEffect`. On save, trim the draft, await the injected function, then update both saved and draft values from `result.tailscale_ip`. On failure, retain the old saved value and expose the error message.

Derive the host as:

```typescript
const host = gateway
  ? networkBind && savedTailscaleIp
    ? gatewayUrlForIp(savedTailscaleIp, gateway.port)
    : networkBind
      ? null
      : `http://${gateway.host}:${gateway.port}`
  : fallbackHost;
```

Before copying in network mode, if `host` is `null`, set the inline error, focus the input, and return without writing to the clipboard. Render the editor only when `networkBind` is true, and keep the gateway-stopped warning behavior unchanged.

- [ ] **Step 5: Wire production dependencies and style the editor**

In `DiagnosticsPage`, pass:

```tsx
loadGatewaySettings={getGatewaySettings}
saveTailscaleIp={saveGatewayTailscaleIp}
```

Import the new client function. Add compact responsive styles for `.connection-ip-editor`, its label/input/button row, `.connection-ip-feedback`, and error/success variants. Reuse existing color variables and focus treatment.

- [ ] **Step 6: Run focused UI tests**

Run: `npm test --prefix frontend -- --run src/features/connections/connections.test.tsx src/features/connections/connectionCommands.test.ts`

Expected: all focused tests pass and no test expects `<IP_TAILSCALE>`.

- [ ] **Step 7: Commit the UI unit**

```bash
git add frontend/src/features/connections/ConnectionsPage.tsx frontend/src/features/connections/connections.test.tsx frontend/src/features/diagnostics/DiagnosticsPage.tsx frontend/src/styles/app.css
git commit -m "feat: configure persistent Tailscale IP in connections"
```

---

### Task 5: Documentation, regression gauntlet, and browser QA

**Files:**
- Modify: `docs/persistence.md`
- Modify: `docs/api-contract.md`
- Modify: `docs/development-setup.md`
- Modify: `docs/roadmap.md`

**Interfaces:**
- Consumes: completed backend and frontend feature.
- Produces: user/developer documentation and verified release-ready behavior.

- [ ] **Step 1: Update documentation with exact behavior**

Document `gateway.tailscale_ip`, the dedicated endpoint, IP-only validation, IPv6 URL brackets, persistence locations on both operating systems, and the rule that `0.0.0.0` is a bind address while the saved IP is the client address. Remove instructions that tell users to manually substitute `<IP_TAILSCALE>` in the app-generated command.

- [ ] **Step 2: Run the backend gauntlet**

Run: `uv run pytest -q`

Expected: all backend tests pass.

- [ ] **Step 3: Run the frontend gauntlet twice**

Run: `npm test --prefix frontend -- --run`

Run the same command a second time.

Expected: both complete runs pass, including load, save, blocked copy, macOS command, and Windows command coverage.

- [ ] **Step 4: Run static and production checks**

Run: `npm run typecheck --prefix frontend`

Run: `npm run build --prefix frontend`

Run: `uv run python scripts/build_backend.py`

Expected: TypeScript reports no errors, Vite builds the frontend, and PyInstaller builds the backend.

- [ ] **Step 5: Run browser QA against the local application**

Start the latest project version, open **Conectar**, select network bind, and verify:

1. Empty saved IP blocks copying and focuses the field.
2. `mac.tailnet.ts.net` is rejected with the backend message.
3. `100.87.71.48` saves and survives a full page reload.
4. macOS/Linux copies `export OLLAMA_HOST=http://100.87.71.48:11435`.
5. Windows copies `$env:OLLAMA_HOST="http://100.87.71.48:11435"`.
6. Returning to local bind copies `127.0.0.1` while the saved IP remains available after switching back.
7. Light and dark themes remain readable at desktop and narrow widths.

- [ ] **Step 6: Request a final code review**

Review the complete diff against `docs/superpowers/specs/2026-10-02-persistent-tailscale-ip-design.md`. Resolve every Critical or Important finding and rerun the affected tests.

- [ ] **Step 7: Commit documentation and QA record**

```bash
git add docs/persistence.md docs/api-contract.md docs/development-setup.md docs/roadmap.md
git commit -m "docs: explain persistent Tailscale connection IP"
```

Do not publish a release unless the user separately requests release publication after reviewing the locally verified result.
