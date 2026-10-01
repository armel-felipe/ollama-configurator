# Operational State Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a compact operational summary that makes application, gateway, saved configuration, applied configuration, and runtime verification states understandable without moving configuration controls out of the main flow.

**Architecture:** Keep `DiagnosticsPage` as the composition root. Child surfaces continue owning their form controls and API operations, but publish a small operational snapshot and their contextual action to the parent. A pure status derivation module maps those snapshots to four user-facing indicators. `OperationalStatusSummary` renders the result and invokes the action supplied by the owning child, so it never becomes a second source of truth.

**Tech Stack:** React 18, TypeScript, Vitest, Testing Library, existing API client and CSS token system.

## Global Constraints

- Preserve the existing light theme as the default and retain dark-theme support.
- Keep the main configuration surfaces on the same page; the summary is not a new route.
- Distinguish “salvo”, “aplicado” and “confirmado no runtime” in copy and state.
- Never use color without an equivalent textual status.
- Do not offer stop/restart controls for a gateway reported as `external`.
- Do not add a second API source or change the gateway/server persistence contract.
- Keep the existing navigation targets and the already-corrected workspace selection behavior.

---

### Task 1: Define the pure operational state model

**Files:**
- Create: `frontend/src/features/status/operationalStatus.ts`
- Create: `frontend/src/features/status/operationalStatus.test.ts`

**Interfaces:**

```ts
import type { GatewayStatus, RuntimeStatus, ServerSettingsState } from "../../api/client";

export type OperationalIndicator =
  | "active"
  | "unavailable"
  | "stopped"
  | "starting"
  | "external"
  | "error"
  | "saved"
  | "dirty"
  | "pending"
  | "applied"
  | "unverified"
  | "divergent";

export type OperationalAction = {
  label: string;
  target: "application" | "gateway" | "server" | "model" | "diagnostics";
  run: () => void | Promise<void>;
};

export type OperationalStatus = {
  application: { state: "active" | "unavailable"; label: string; detail: string };
  gateway: { state: OperationalIndicator; label: string; detail: string };
  configuration: { state: "saved" | "dirty" | "pending"; label: string; detail: string };
  runtime: { state: "applied" | "unverified" | "divergent"; label: string; detail: string };
  primaryAction: OperationalAction | null;
};

export type OperationalInputs = {
  ollamaAvailable: boolean;
  gateway: GatewayStatus | null;
  gatewayError?: string | null;
  server: Pick<ServerSettingsState, "available" | "pending_restart"> | null;
  serverDirty: boolean;
  serverError?: string | null;
  runtime: RuntimeStatus | null;
  runtimeError?: string | null;
  actions: {
    startGateway?: OperationalAction;
    retryGateway?: OperationalAction;
    saveServer?: OperationalAction;
    applyServer?: OperationalAction;
    retryServer?: OperationalAction;
    applyModel?: OperationalAction;
    retryRuntime?: OperationalAction;
  };
};

export function deriveOperationalStatus(input: OperationalInputs): OperationalStatus;
```

- [ ] **Step 1: Write failing tests for the status precedence rules.** Cover:
  `ollamaAvailable=false`, stopped/starting/running/external/error gateway,
  dirty server state, pending restart, confirmed runtime, divergent runtime,
  and the priority order `error > dirty > pending > gateway stopped > runtime`.

```ts
it("prioritizes unsaved server changes over an otherwise healthy gateway", () => {
  const status = deriveOperationalStatus({
    ollamaAvailable: true,
    gateway: { state: "running", host: "127.0.0.1", port: 11435 },
    server: { available: true, pending_restart: false },
    serverDirty: true,
    runtime: null,
    actions: { saveServer: { label: "Salvar configurações", target: "server", run: vi.fn() } },
  });

  expect(status.configuration.state).toBe("dirty");
  expect(status.primaryAction?.label).toBe("Salvar configurações");
});
```

- [ ] **Step 2: Run the focused test and verify it fails for the missing module.**

Run: `npm test -- --run src/features/status/operationalStatus.test.ts`

Expected: FAIL because `deriveOperationalStatus` does not exist yet.

- [ ] **Step 3: Implement only the pure derivation function.** Keep the function free of React, DOM, fetch calls, and side effects. Always return text for every indicator. Use `external` as a distinct state and never assign a stop action to it.

- [ ] **Step 4: Run the focused test and verify all precedence cases pass.**

Run: `npm test -- --run src/features/status/operationalStatus.test.ts`

Expected: PASS.

- [ ] **Step 5: Commit the isolated state model.**

```bash
git add frontend/src/features/status/operationalStatus.ts frontend/src/features/status/operationalStatus.test.ts
git commit -m "feat: define operational status model"
```

### Task 2: Build the summary presentation

**Files:**
- Create: `frontend/src/features/status/OperationalStatusSummary.tsx`
- Create: `frontend/src/features/status/operationalStatusSummary.test.tsx`
- Modify: `frontend/src/styles/app.css`

**Interfaces:**

```tsx
type Props = {
  status: OperationalStatus;
};

export function OperationalStatusSummary({ status }: Props): JSX.Element;
```

- [ ] **Step 1: Write failing component tests.** Assert four accessible status groups, visible state text, the primary action when present, no primary action for a healthy fully-applied state, and explanatory text for `external` gateway ownership.

```tsx
it("renders one contextual action and four readable status indicators", () => {
  render(<OperationalStatusSummary status={fixtureWithPendingServer} />);

  expect(screen.getByRole("region", { name: /estado operacional/i })).toBeInTheDocument();
  expect(screen.getByText(/gateway 11435/i)).toBeInTheDocument();
  expect(screen.getByText(/alterações aguardando aplicação/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Aplicar no Ollama" })).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the focused component test and verify it fails.**

Run: `npm test -- --run src/features/status/operationalStatusSummary.test.tsx`

Expected: FAIL because the component does not exist.

- [ ] **Step 3: Implement the summary with semantic markup.** Render a labeled region, four compact cards, textual status labels, details, and one primary button. Add `aria-live="polite"` only to the summary status line so transitions are announced without repeatedly reading every card.

- [ ] **Step 4: Add light/dark and narrow-viewport styles.** Use existing CSS variables, preserve readable contrast, keep cards in one row when space permits, and stack them without horizontal scrolling below the existing mobile breakpoint. Do not add gradients or introduce a second visual language.

- [ ] **Step 5: Run the focused component test and verify it passes.**

Run: `npm test -- --run src/features/status/operationalStatusSummary.test.tsx`

Expected: PASS.

- [ ] **Step 6: Commit the isolated presentation.**

```bash
git add frontend/src/features/status/OperationalStatusSummary.tsx frontend/src/features/status/operationalStatusSummary.test.tsx frontend/src/styles/app.css
git commit -m "feat: add operational status summary"
```

### Task 3: Publish server, gateway, and model state to the composition root

**Files:**
- Modify: `frontend/src/features/server/ServerSettingsPage.tsx`
- Modify: `frontend/src/features/gateway/GatewayControls.tsx`
- Modify: `frontend/src/features/models/ModelSettingsPage.tsx`
- Modify: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Modify: `frontend/src/features/server/serverSettings.test.tsx`
- Modify: `frontend/src/features/gateway/gatewayControls.test.tsx`
- Modify: `frontend/src/features/models/modelSettings.test.tsx`

**Interfaces:**

```ts
type ServerViewState = {
  loaded: boolean;
  available: boolean;
  pendingRestart: boolean;
  dirty: boolean;
  error: string | null;
};

type ModelViewState = {
  selected: boolean;
  dirty: boolean;
  runtime: RuntimeStatusData | null;
  error: string | null;
};

type PublishedStateProps = {
  onStateChange?: (state: ServerViewState | GatewayStatus | ModelViewState) => void;
  onActionChange?: (action: OperationalAction | null) => void;
};
```

- [ ] **Step 1: Add failing tests that observe published state.** Verify server emits `dirty=true` after a field change and `pendingRestart=true` after save; gateway emits `external` without a stop action; model emits runtime confirmation after apply and clears runtime after an edit.

- [ ] **Step 2: Run the focused tests and verify the new publication assertions fail.**

Run: `npm test -- --run src/features/server/serverSettings.test.tsx src/features/gateway/gatewayControls.test.tsx src/features/models/modelSettings.test.tsx`

Expected: FAIL only on the new callback assertions.

- [ ] **Step 3: Add callback props and publish snapshots from existing state transitions.** Do not duplicate fetches. Callbacks should be updated on initial load, user edits, saves, applies, retries, and errors. Keep existing child UI and handlers intact.

- [ ] **Step 4: Pass the callbacks from `DiagnosticsPage` and store the latest snapshots in parent state.** Use `useState` in `DiagnosticsPage`; initialize missing child states as `null` so the summary can say “carregando”/“não verificado” instead of claiming success.

- [ ] **Step 5: Run the focused tests and verify they pass.**

Run: `npm test -- --run src/features/server/serverSettings.test.tsx src/features/gateway/gatewayControls.test.tsx src/features/models/modelSettings.test.tsx`

Expected: PASS.

- [ ] **Step 6: Commit the state publication wiring.**

```bash
git add frontend/src/features/server/ServerSettingsPage.tsx frontend/src/features/gateway/GatewayControls.tsx frontend/src/features/models/ModelSettingsPage.tsx frontend/src/features/diagnostics/DiagnosticsPage.tsx frontend/src/features/server/serverSettings.test.tsx frontend/src/features/gateway/gatewayControls.test.tsx frontend/src/features/models/modelSettings.test.tsx
git commit -m "feat: publish runtime state to workspace"
```

### Task 4: Integrate derivation, summary, and contextual actions

**Files:**
- Modify: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Create: `frontend/src/features/status/operationalIntegration.test.tsx`

- [ ] **Step 1: Write failing integration tests for the complete transitions.** Cover:
  loaded healthy state;
  unsaved server change showing “Salvar configurações”;
  saved pending restart showing “Aplicar no Ollama”;
  external gateway with explanatory text and no stop action;
  divergent model runtime showing “Reaplicar perfil”.

- [ ] **Step 2: Run the integration test and verify it fails because the summary is not mounted.**

Run: `npm test -- --run src/features/status/operationalIntegration.test.tsx`

Expected: FAIL because `OperationalStatusSummary` is not present in `DiagnosticsPage`.

- [ ] **Step 3: Derive `OperationalStatus` in `DiagnosticsPage` and render the summary directly below the page heading.** Pass the child-published callbacks into `deriveOperationalStatus`, preserving the existing server, gateway, model, and reset sections below it.

- [ ] **Step 4: Make the summary action call the owning child handler.** When the action is “salvar”, “aplicar”, “iniciar gateway”, or “reaplicar perfil”, invoke the callback published by that child. If the action is navigation-only, scroll to the owning section and focus its primary control.

- [ ] **Step 5: Remove contradictory copy from existing action rows.** The server row must not show “Perfil global salvo” while `pending_restart` is true; the model row must not show “Perfil salvo” while it is dirty. Reuse the derived state labels where possible.

- [ ] **Step 6: Run the integration test and verify it passes.**

Run: `npm test -- --run src/features/status/operationalIntegration.test.tsx`

Expected: PASS.

- [ ] **Step 7: Commit the integrated behavior.**

```bash
git add frontend/src/features/diagnostics/DiagnosticsPage.tsx frontend/src/features/status/operationalIntegration.test.tsx frontend/src/features/server/ServerSettingsPage.tsx frontend/src/features/models/ModelSettingsPage.tsx
git commit -m "feat: clarify operational state in workspace"
```

### Task 5: Run the project gauntlet and browser UX QA

**Files:**
- Modify: only files required by verified defects from this task.

- [ ] **Step 1: Run all automated checks.**

```bash
cd frontend
npm test -- --run
npm run typecheck
npm run build
cd ..
uv run pytest -q
uv run ruff check backend tests
uv run mypy backend
```

Expected: frontend tests, typecheck, build, backend tests, Ruff, and mypy all pass. If `npm run lint` remains unavailable because `eslint` is not installed, record it as an environment gap rather than silently claiming it passed.

- [ ] **Step 2: Start the launcher and inspect the light-theme desktop flow.** Confirm the summary is visible before the settings, the default light theme is readable, the current gateway state is explicit, and only one contextual action is prominent.

- [ ] **Step 3: Exercise state transitions in the browser.** Change a global value without saving, save it, observe pending restart, apply it, select a model, edit Thinking or context, save, apply, and confirm runtime. Reload between stages where persistence is part of the test.

- [ ] **Step 4: Exercise error and ownership states.** Verify local configuration load failure has retry plus application restart recovery, verify an external gateway has no destructive stop action, and verify the UI explains the next step for a disconnected gateway.

- [ ] **Step 5: Check dark theme, narrow viewport, keyboard focus, and console logs.** Ensure status text remains visible in both themes, cards stack without horizontal overflow, action buttons are keyboard reachable, and the browser console has no errors or warnings.

- [ ] **Step 6: Fix only defects found in this bounded QA pass, rerun the relevant focused test, then rerun the full gauntlet once.**

- [ ] **Step 7: Commit the verified QA fixes.**

```bash
git add frontend backend tests docs
git commit -m "test: verify operational state UX"
```
