# Ollama Configurator UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Replace the prototype-like frontend with a clean, professional profile editor that defaults to light theme, supports a persistent dark theme, and separates daily configuration from runtime diagnostics.

**Architecture:** Keep the existing FastAPI contracts and model-setting services unchanged. Rebuild the React composition around an `AppShell` with a persistent theme controller, a compact workspace navigation, a focused model profile editor, and a secondary diagnostics surface. Use CSS custom properties for both themes so components do not branch on hard-coded colors.

**Tech Stack:** React 18, TypeScript, Vite, Vitest, Testing Library, CSS custom properties, semantic HTML.

## Global Constraints

- Tema claro é o padrão inicial; tema escuro é alternável e persistido localmente.
- A interface deve responder: modelo configurado, estado salvo/efetivo e próxima ação.
- Context presets permanecem 16K, 32K, 64K, 128K e 256K, com valor personalizado.
- Reasoning/Thinking continua dependente dos valores declarados pelo modelo.
- Runtime efetivo é somente confirmação; divergência nunca pode ser apresentada como sucesso.
- O teste de inferência permanece disponível em Diagnóstico avançado, fora do fluxo principal.
- Não alterar contratos Ollama, persistência backend ou lógica de aplicação do runtime nesta rodada.
- Todos os controles devem ter nome acessível, foco visível e operação por teclado.
- Desktop macOS/Windows é prioridade; viewport estreito deve permanecer utilizável.

---

## Mapa de arquivos

- Create `frontend/src/features/shell/AppShell.tsx`: composição da navegação, cabeçalho, tema e área de conteúdo.
- Create `frontend/src/features/shell/ThemeProvider.tsx`: estado de tema, persistência local e aplicação de `data-theme`.
- Create `frontend/src/features/shell/theme.test.tsx`: testes de padrão claro, alternância e persistência.
- Create `frontend/src/features/shell/appShell.test.tsx`: testes de navegação e labels acessíveis.
- Create `frontend/src/styles/app.css`: tokens, layout, componentes e temas claro/escuro.
- Modify `frontend/src/main.tsx`: importar estilos globais e montar o provider.
- Modify `frontend/src/App.tsx`: usar `AppShell` e separar as superfícies de Modelos, Servidor e Diagnóstico.
- Create `frontend/src/features/models/ModelWorkspace.tsx`: seleção de modelo e editor no mesmo fluxo de trabalho.
- Create `frontend/src/features/models/ModelWorkspace.test.tsx`: estados sem modelo, modelo selecionado e seleção persistente em memória.
- Modify `frontend/src/features/models/ModelsList.tsx`: transformar a lista em navegação lateral compacta, mantendo nomes e seleção acessíveis.
- Modify `frontend/src/features/models/ModelSettingsPage.tsx`: usar a composição visual nova e separar perfil, ação primária e confirmação de runtime.
- Modify `frontend/src/features/models/ParameterControl.tsx`: controles segmentados, toggle e campo customizado com estados explícitos.
- Modify `frontend/src/features/models/RuntimeStatus.tsx`: bloco compacto de solicitado/efetivo e estados sem depender só de cor.
- Create `frontend/src/features/diagnostics/AdvancedDiagnostics.tsx`: conter teste de inferência e explicação da limitação de `ollama run`.
- Create `frontend/src/features/diagnostics/advancedDiagnostics.test.tsx`: teste de renderização recolhida e execução explícita.
- Modify `frontend/src/features/diagnostics/DiagnosticsPage.tsx`: reduzir diagnóstico inicial e encaminhar a superfície avançada.
- Modify `frontend/src/App.test.tsx` e testes existentes: atualizar expectativas sem remover cobertura funcional.

---

### Task 1: Shell visual, temas e navegação principal

**Files:** os arquivos de shell, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/styles/app.css` e testes listados no mapa.

**Interfaces:**

- `Theme = "light" | "dark"`.
- `ThemeProvider({ children }: { children: React.ReactNode }): JSX.Element`.
- `useTheme(): { theme: Theme; toggleTheme(): void }`.
- `AppShell({ children, selectedSection, onSectionChange }): JSX.Element`.
- `localStorage` key: `ollama-configurator.theme`.

- [ ] **Step 1: Write failing tests for theme behavior.**

  Teste que, sem preferência armazenada, `document.documentElement.dataset.theme` seja `light`; ao ativar o controle, torne-se `dark`; ao remontar, a preferência permaneça `dark`; e o botão exponha `aria-label="Alternar para tema claro"` no tema escuro.

- [ ] **Step 2: Run the focused tests and verify failure.**

  Run: `npm test -- --run src/features/shell/theme.test.tsx`

  Expected: FAIL because `ThemeProvider`, `useTheme` and the shell controls do not exist.

- [ ] **Step 3: Implement tokens and shell.**

  Define `:root` with light tokens and `[data-theme="dark"]` with dark tokens for `--surface`, `--surface-raised`, `--text`, `--text-muted`, `--border`, `--accent`, `--success`, `--warning`, `--danger`, focus ring, radius and spacing. Render a top bar with product name, current model label and a text-plus-icon theme button. Use a left navigation with `Modelos`, `Servidor` and `Diagnóstico`; the selected item must use `aria-current="page"` and a non-color visual indicator.

- [ ] **Step 4: Run tests and build.**

  Run: `npm test -- --run src/features/shell/theme.test.tsx src/features/shell/appShell.test.tsx && npm run typecheck`

  Expected: all focused tests pass and TypeScript exits with code 0.

- [ ] **Step 5: Commit the shell.**

  Run: `git add frontend/src/main.tsx frontend/src/App.tsx frontend/src/features/shell frontend/src/styles/app.css && git commit -m "feat: add configurator shell and theme system"`

### Task 2: Modelo como workspace principal

**Files:** `ModelWorkspace.tsx`, `ModelsList.tsx`, `ModelWorkspace.test.tsx`, `App.tsx`.

**Interfaces:**

- `ModelWorkspace({ models, selectedModel, onSelect, children }): JSX.Element`.
- Model selection remains `string | undefined`; no new backend endpoint.

- [ ] **Step 1: Write failing tests for workspace states.**

  Cover: installed models render as buttons with `aria-pressed`; selecting one calls `onSelect` exactly once; an empty list renders a useful installation/refresh message; and no selected model renders “Selecione um modelo para configurar” in the main content area.

- [ ] **Step 2: Run the focused test and verify failure.**

  Run: `npm test -- --run src/features/models/ModelWorkspace.test.tsx`

  Expected: FAIL because the workspace component does not exist.

- [ ] **Step 3: Implement the workspace composition.**

  Put the model list in the shell’s left workspace column. Keep model identity, runner and loaded state in the main header when runtime data exists. Do not put hardware, Ollama version, inference textarea or reset controls in the primary model workspace. Preserve keyboard navigation and an active-row indicator independent of color.

- [ ] **Step 4: Update App composition and tests.**

  Replace the current single long `DiagnosticsPage` flow with `AppShell` and a section switch. `ModelWorkspace` owns the model selection surface; the existing settings page renders only after selection. Keep data loading and API calls unchanged.

- [ ] **Step 5: Run frontend regression tests.**

  Run: `npm test -- --run src/features/models src/features/diagnostics/diagnostics.test.tsx src/App.test.tsx && npm run typecheck`

  Expected: all existing functional expectations pass with the new composition.

### Task 3: Editor de perfil e controles inequívocos

**Files:** `ModelSettingsPage.tsx`, `ParameterControl.tsx`, their tests, and `app.css`.

**Interfaces:** preserve existing props and API callbacks; visual changes must not change `saveSettings` or `applySettings` payloads.

- [ ] **Step 1: Write failing tests for interaction states.**

  Add tests that presets select exactly one context value, custom input enables the free numeric field, default disables the override and sends `"default"` on save, thinking false remains boolean `false`, and the primary action labels states as `Salvar e aplicar`, `Aplicando…`, or `Aplicado`/divergente based on runtime.

- [ ] **Step 2: Run focused tests and verify the expected failures.**

  Run: `npm test -- --run src/features/models/modelSettings.test.tsx src/features/models/runtimeStatus.test.tsx`

  Expected: new state and accessible-control assertions fail before the redesign implementation.

- [ ] **Step 3: Implement the profile editor layout.**

  Group controls into `Context window`, `Reasoning / Thinking` and `Advanced parameters`. Render context presets as a semantic radio group or `role="radiogroup"` with selected state; render a custom value field beside a clear `Personalizado` action; render boolean thinking as a native switch/checkbox with visible `Ligado`/`Desligado`; keep temperature, max output and keep alive visually secondary. Use one primary action and one secondary reset/default action per parameter group.

- [ ] **Step 4: Implement state copy and dirty behavior.**

  Keep “Alterações não salvas” after an edit, “Configurações salvas” only immediately after save, “Aplicando no Ollama…” during apply, “Runtime confirmado” only when requested/effective values match, and “Aplicação não confirmada” when they differ. Clear transient save confirmation on the next edit as already required by the existing behavior.

- [ ] **Step 5: Run tests and typecheck.**

  Run: `npm test -- --run src/features/models/modelSettings.test.tsx src/features/models/runtimeStatus.test.tsx && npm run typecheck`

  Expected: all model settings tests pass and no type errors are reported.

### Task 4: Runtime compacto e diagnóstico avançado

**Files:** `RuntimeStatus.tsx`, `AdvancedDiagnostics.tsx`, `advancedDiagnostics.test.tsx`, `DiagnosticsPage.tsx`, `InferenceTestPanel.tsx`.

- [ ] **Step 1: Write failing tests for runtime and diagnostics hierarchy.**

  Test that runtime shows `Contexto solicitado` and `Contexto efetivo`, exposes an alert for mismatch, and that the inference panel is not rendered in the primary model workspace but appears after opening `Diagnóstico avançado`.

- [ ] **Step 2: Implement the compact runtime block.**

  Replace the verbose runtime section with a compact status row or panel containing model loaded state, requested/effective context, runner, thinking and a textual status label. Use `role="status"` for successful application and `role="alert"` for divergence/error.

- [ ] **Step 3: Implement advanced diagnostics disclosure.**

  Render inference inside a collapsed `details` or explicit disclosure under Diagnóstico avançado. Keep its explanation: it validates the profile sent by the application and does not control an independent interactive `ollama run` session. Preserve the existing prompt, response, thinking and error behavior.

- [ ] **Step 4: Run focused tests.**

  Run: `npm test -- --run src/features/models/inferenceTest.test.tsx src/features/diagnostics/advancedDiagnostics.test.tsx src/features/models/runtimeStatus.test.tsx && npm run typecheck`

  Expected: inference remains covered while no longer occupying the primary configuration flow.

### Task 5: Responsive layout, accessibility and visual QA

**Files:** `frontend/src/styles/app.css`, all changed frontend components and tests.

- [ ] **Step 1: Add responsive and accessibility tests.**

  Assert that navigation items, theme button, context controls and thinking switch have accessible names; focus styles are present in CSS; and the main content remains ordered correctly when the viewport is narrow.

- [ ] **Step 2: Implement responsive rules.**

  At desktop widths, use a compact sidebar plus main editor. At narrow widths, collapse the sidebar to a top navigation/drawer pattern, keep the model title and primary action visible, stack parameter groups, and prevent horizontal scrolling.

- [ ] **Step 3: Run the complete project gauntlet.**

  Run from the repository root:

  ```bash
  ./.venv/bin/pytest -q
  cd frontend && npm test -- --run && npm run typecheck && npm run build
  cd .. && ./.venv/bin/ruff check backend tests
  ```

  Expected: backend tests pass, all frontend tests pass, typecheck/build pass and Ruff reports no violations.

- [ ] **Step 4: Run visual QA in both themes.**

  Start the frontend and inspect the first viewport at desktop and narrow widths. Verify: light theme is the initial default; dark theme toggles and survives reload; selected model is obvious; context presets look like a single control; thinking switch clearly shows on/off; save/apply states are readable; runtime mismatch is impossible to mistake for success; inference is absent from the primary workspace and available under advanced diagnostics.

- [ ] **Step 5: Run the Impeccable detector once on changed UI targets.**

  Run:

  ```bash
  /Users/mac/.agents/skills/impeccable/scripts/impeccable detect --json frontend/src/App.tsx frontend/src/main.tsx frontend/src/features frontend/src/styles/app.css
  ```

  Fix mechanical findings that violate this specification, then rerun the frontend tests and build once.

- [ ] **Step 6: Commit the redesign.**

  Run: `git add frontend/src frontend/package.json frontend/package-lock.json && git commit -m "feat: redesign configurator interface"`

## Acceptance checklist

- [ ] A first-time user sees a calm light interface with a clear Modelos workspace.
- [ ] Theme can be changed from the top bar and persists after reload.
- [ ] A selected model, saved profile and effective runtime are visually distinct.
- [ ] Context and thinking controls are recognizable without reading implementation details.
- [ ] The primary configuration flow contains no inference prompt.
- [ ] Advanced diagnostics can still run the inference verification.
- [ ] The UI shows requested versus effective context and never claims success on mismatch.
- [ ] Desktop and narrow layouts remain usable with keyboard and assistive labels.
- [ ] Backend contracts and runtime behavior are unchanged by this visual-only plan.

