# Ollama Connections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Conectar workspace that reproduces the supplied Ollama-style app grid and generates copy-ready gateway commands for all fifteen clients.

**Architecture:** Keep command generation pure and independently tested in a small frontend module. Add a presentational `ConnectionsPage` that consumes the existing model list, selected model, and gateway status from `DiagnosticsPage`; extend `AppShell` with a Conectar section and let the existing diagnostic page remain the source of runtime state. No new backend endpoint is needed because gateway status already exposes host and port.

**Tech Stack:** React 18, TypeScript, Vite, Vitest, Testing Library, existing CSS token system.

## Global Constraints

- The default local gateway is `http://127.0.0.1:11435`.
- macOS/Linux output must use two lines beginning with `export OLLAMA_HOST=...`.
- Windows PowerShell output must use two lines beginning with `$env:OLLAMA_HOST="..."`.
- Integration cards use `ollama launch <app> --model <model>`.
- Terminal uses `ollama run <model> --verbose`.
- No feature in this task may attempt to open a native Terminal window.
- Light theme remains the default and dark theme must be supported.

---

### Task 1: Add pure connection command catalog and generator

**Files:**
- Create: `frontend/src/features/connections/connectionCommands.ts`
- Create: `frontend/src/features/connections/connectionCommands.test.ts`

**Interfaces:**
- Produces `connectionClients`, `ShellKind`, `buildConnectionCommand(clientId, model, shell, host)` for the page.

- [ ] **Step 1: Write failing tests** for all fifteen client mappings, terminal verbose behavior, both shells, host interpolation, and model names containing tags.
- [ ] **Step 2: Run the focused test and verify it fails** with the missing module.
- [ ] **Step 3: Implement the catalog and generator** with typed client ids, labels, descriptions, and the exact command rules from the design spec.
- [ ] **Step 4: Run the focused test and verify it passes.**

### Task 2: Add the ConnectionsPage UI

**Files:**
- Create: `frontend/src/features/connections/ConnectionsPage.tsx`
- Create: `frontend/src/features/connections/connections.test.tsx`
- Modify: `frontend/src/styles/app.css`

**Interfaces:**
- Props: `models`, `selectedModel`, `gateway`, `onSelectModel`.
- Uses `connectionClients` and `buildConnectionCommand` from Task 1.

- [ ] **Step 1: Write failing UI tests** for the fifteen cards, selected card state, model-empty state, shell selector, command preview, gateway stopped warning, and copy feedback.
- [ ] **Step 2: Run the focused UI test and verify it fails.**
- [ ] **Step 3: Implement the page** with accessible buttons, responsive two-column grid, command panel, status message, and clipboard action.
- [ ] **Step 4: Add light/dark and mobile styles** using existing variables, without introducing a second design system.
- [ ] **Step 5: Run the focused UI test and verify it passes.**

### Task 3: Integrate the section with existing app state

**Files:**
- Modify: `frontend/src/features/shell/AppShell.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/features/diagnostics/DiagnosticsPage.tsx`
- Modify: `frontend/src/App.test.tsx`
- Modify: `frontend/src/features/shell/appShell.test.tsx`

**Interfaces:**
- Extend `WorkspaceSection` with `connections`.
- `DiagnosticsPage` keeps model selection and gateway state and renders `ConnectionsPage` when the active section is connections.

- [ ] **Step 1: Add failing navigation/integration tests** for the Conectar link and command generation from the selected model and gateway status.
- [ ] **Step 2: Run the focused tests and verify failure.**
- [ ] **Step 3: Implement section routing/state integration** without changing model reload effects or gateway lifecycle behavior.
- [ ] **Step 4: Run all frontend tests and verify they pass.**

### Task 4: Documentation and visual QA

**Files:**
- Modify: `docs/roadmap.md`
- Modify: `README.md` if the local usage section needs the new Conectar workflow.
- Create: `.impeccable/review/desktop.png`
- Create: `.impeccable/review/mobile.png`

- [ ] **Step 1: Run frontend lint, typecheck, build and tests.**
- [ ] **Step 2: Run the dev launcher and inspect the screen at desktop and mobile widths.**
- [ ] **Step 3: Verify all fifteen cards, copy action, shell switching, selected model switching, gateway stopped warning, light theme and dark theme.**
- [ ] **Step 4: Run the Impeccable detector once on changed UI files and fix mechanical findings.**
- [ ] **Step 5: Run backend regression tests to confirm no API or launcher regression.**
- [ ] **Step 6: Record implementation status and QA evidence in the roadmap.**

## Self-review checklist

- All fifteen supplied card mappings are represented in Task 1 and Task 2.
- Terminal has `--verbose` and integrations have `--model`.
- Both shell syntaxes are covered by tests.
- Host and model are dynamic rather than hard-coded in the rendered command.
- The page works when no model is selected and when the gateway is stopped.
- No automatic native Terminal launch is introduced.
- Desktop, mobile, light, and dark visual states are part of QA.
