# Shell com Rolagem Independente e Ícones de Marca Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar a moldura desktop em duas áreas de rolagem independentes e substituir os ícones genéricos por assets locais de marca, preservando comportamento, temas e acessibilidade.

**Architecture:** `AppShell` controla uma moldura com `sidebar` e `workspace-content` como regiões de viewport independentes. A navegação mantém a marca fora da área rolável e concentra os itens variáveis em uma região interna. Os cards de conexão consomem um mapa tipado de assets SVG locais; a origem e os termos de cada asset ficam documentados, sem requisições remotas em runtime.

**Tech Stack:** React 18, TypeScript, Vite, CSS existente em `frontend/src/styles/app.css`, Vitest, Testing Library e assets SVG locais.

## Global Constraints

- Desktop usa duas colunas com altura da janela; marca, navegação e status do gateway permanecem acessíveis enquanto o conteúdo da direita rola.
- Mobile volta a uma coluna única e não pode criar rolagem horizontal ou conteúdo inacessível.
- Usar assets oficiais locais; sem hotlink; registrar fonte e licença/termos de uso.
- Quando uma marca não tiver asset oficial reutilizável ou licença verificável, usar fallback neutro e documentar a decisão.
- O texto dos nomes permanece visível; ícones decorativos não substituem a identificação textual.
- Preservar temas claro/escuro, seleção de cards, cópia automática, estado “Copiado”, gateway e acessibilidade.
- Não alterar gateway, persistência, formulários de parâmetros, comandos Ollama, lista de clientes ou instalador.
- Não incluir no commit alterações anteriores não relacionadas que já estejam presentes no worktree.
- Antes de cada commit, comparar `git diff` com o estado anterior; quando um arquivo já estiver modificado, usar `git add -p` para selecionar somente os hunks desta etapa.

---

### Task 1: Fixar o contrato estrutural da moldura

**Files:**
- Modify: `frontend/src/features/shell/AppShell.tsx`
- Modify: `frontend/src/App.tsx`
- Test: `frontend/src/features/shell/appShell.test.tsx`
- Test: `frontend/src/App.test.tsx`

**Interfaces:**
- Consumes: `WorkspaceSection`, `children` e `onSectionChange` atuais.
- Produces: regiões identificáveis `app-shell`, `sidebar`, `sidebar-scroll` e `workspace-content-scroll`.

- [ ] **Step 1: Escrever o teste que falha**

Em `appShell.test.tsx`, manter os testes existentes e acrescentar:

```tsx
expect(screen.getByTestId("app-shell")).toBeInTheDocument();
expect(screen.getByTestId("sidebar")).toBeInTheDocument();
expect(screen.getByTestId("sidebar-scroll")).toContainElement(
  screen.getByRole("navigation", { name: /workspace/i }),
);
expect(screen.getByTestId("workspace-content-scroll")).toContainElement(
  screen.getByRole("heading", { name: /área de trabalho/i }),
);
```

Em `App.test.tsx`, verificar que a seção escolhida continua dentro de `workspace-content-scroll` após uma mudança de navegação.

- [ ] **Step 2: Confirmar a falha**

```bash
cd frontend && npm test -- --run src/features/shell/appShell.test.tsx src/App.test.tsx
```

Esperado: FAIL porque a hierarquia e os `data-testid` ainda não existem.

- [ ] **Step 3: Implementar a hierarquia mínima**

Em `AppShell.tsx`, separar marca e conteúdo rolável sem duplicar o `OllamaLogo`:

```tsx
<div className="app-shell" data-testid="app-shell">
  <div className="app-frame">
    <aside className="app-sidebar" data-testid="sidebar">
      <header className="sidebar-brand">{brand}</header>
      <div className="sidebar-scroll" data-testid="sidebar-scroll">
        <nav aria-label="Workspace">{navigation}</nav>
        <div className="nav-footer">{gatewayStatus}</div>
      </div>
    </aside>
    <main className="workspace-content" data-testid="workspace-content-scroll">{children}</main>
  </div>
</div>
```

Em `App.tsx`, manter a seleção por hash e usar somente o alvo da seção dentro do painel direito:

```tsx
const selectSection = (section: WorkspaceSection) => {
  setSelectedSection(section);
  window.requestAnimationFrame(() => {
    document.getElementById(`${section}-section`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
};
```

- [ ] **Step 4: Confirmar a passagem**

```bash
cd frontend && npm test -- --run src/features/shell/appShell.test.tsx src/App.test.tsx
```

Esperado: todos os testes PASS.

- [ ] **Step 5: Commitar**

```bash
git add frontend/src/features/shell/AppShell.tsx frontend/src/App.tsx frontend/src/features/shell/appShell.test.tsx frontend/src/App.test.tsx
git commit -m "refactor: split app shell into scroll regions"
```

---

### Task 2: Implementar as duas rolagens e o layout móvel

**Files:**
- Modify: `frontend/src/styles/app.css`
- Test: `frontend/src/features/shell/appShell.test.tsx`

**Interfaces:**
- Consumes: classes e `data-testid` da Task 1.
- Produces: sidebar fixa, rolagem interna do menu e painel direito rolável no desktop; uma coluna no mobile.

- [ ] **Step 1: Implementar o layout desktop**

Substituir as regras conflitantes da moldura por:

```css
.app-shell { height: 100dvh; min-height: 100vh; overflow: hidden; background: var(--surface); }
.app-frame { display: grid; grid-template-columns: 232px minmax(0, 1fr); height: 100%; min-height: 0; }
.app-sidebar { display: flex; min-height: 0; flex-direction: column; border-right: 1px solid var(--border); background: var(--surface-raised); }
.sidebar-brand { flex: 0 0 auto; padding: 22px 18px; border-bottom: 1px solid var(--border); }
.sidebar-scroll { display: flex; min-height: 0; flex: 1 1 auto; flex-direction: column; overflow-y: auto; overscroll-behavior: contain; padding: 22px 14px 16px; }
.workspace-content { min-width: 0; min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding: 42px clamp(24px, 5vw, 72px) 80px; }
```

Preservar `margin-top: auto` no status do gateway dentro de `sidebar-scroll`, para que ele continue acessível.

- [ ] **Step 2: Implementar o modo móvel**

No breakpoint existente, adaptar os seletores reais para:

```css
@media (max-width: 760px) {
  .app-shell { height: auto; min-height: 100vh; overflow: visible; }
  .app-frame { display: block; height: auto; }
  .app-sidebar { display: block; border-right: 0; }
  .sidebar-brand { padding: 16px; }
  .sidebar-scroll { display: block; overflow: visible; padding: 0; }
  .workspace-nav { display: flex; overflow-x: auto; padding: 8px 12px; border-bottom: 1px solid var(--border); }
  .nav-footer { display: none; }
  .workspace-content { overflow: visible; padding: 28px 16px 56px; }
}
```

Não deixar duas regras concorrentes para o mesmo seletor.

- [ ] **Step 3: Verificar**

```bash
cd frontend && npm run typecheck
cd frontend && npm test -- --run src/features/shell/appShell.test.tsx
cd frontend && npm run build
```

Esperado: typecheck, testes e build PASS.

- [ ] **Step 4: Commitar**

```bash
git add frontend/src/styles/app.css frontend/src/features/shell/appShell.test.tsx
git commit -m "feat: add independent sidebar and content scrolling"
```

---

### Task 3: Criar assets locais e inventário de origem

**Files:**
- Create: `frontend/src/assets/brands/ollama.svg`
- Create: `frontend/src/assets/brands/claude.svg`
- Create: `frontend/src/assets/brands/codex.svg`
- Create: `frontend/src/assets/brands/openclaw.svg`
- Create: `frontend/src/assets/brands/opencode.svg`
- Create: `frontend/src/assets/brands/hermes.svg`
- Create: `frontend/src/assets/brands/droid.svg`
- Create: `frontend/src/assets/brands/pi.svg`
- Create: `frontend/src/assets/brands/cline.svg`
- Create: `frontend/src/assets/brands/copilot.svg`
- Create: `frontend/src/assets/brands/omp.svg`
- Create: `frontend/src/assets/brands/deepseek-harness.svg`
- Create: `frontend/src/assets/brands/poolside.svg`
- Create: `frontend/src/assets/brands/qwen.svg`
- Create: `frontend/src/assets/brands/terminal.svg`
- Create: `frontend/src/assets/brands/brandAssets.ts`
- Create: `docs/assets/connection-icons.md`

**Interfaces:**
- Consumes: `ConnectionClientId` de `frontend/src/features/connections/connectionCommands.ts`.
- Produces: `BrandAsset`, `brandAssets` e `ollamaBrandAsset`.

- [ ] **Step 1: Criar a tabela de origem**

Em `docs/assets/connection-icons.md`, criar uma linha para cada id: `claude`, `codex`, `openclaw`, `opencode`, `hermes`, `hermes-desktop`, `droid`, `pi`, `cline`, `copilot`, `omp`, `dsh`, `pool`, `qwen` e `terminal`. Cada linha deve conter nome exibido, arquivo local, URL de origem, licença/termos verificados, variante de tema e indicação de fallback.

Usar o repositório/página oficial quando o projeto publicar o asset. Quando não publicar, usar uma fonte de marcas com termos claros e marcar `licensed`; não usar um logo redesenhado manualmente como se fosse oficial.

- [ ] **Step 2: Salvar SVGs seguros**

Os SVGs devem ser estáticos, sem script, `foreignObject`, fonte remota ou referência de rede. `terminal.svg` deve ser um símbolo neutro de terminal e ser marcado como `fallback`.

- [ ] **Step 3: Criar o mapa tipado**

Em `brandAssets.ts`, usar imports locais e um mapa completo com estas 15 chaves:

```ts
import type { ConnectionClientId } from "../../features/connections/connectionCommands";
import ollama from "./ollama.svg";
import claude from "./claude.svg";
import codex from "./codex.svg";
import openclaw from "./openclaw.svg";
import opencode from "./opencode.svg";
import hermes from "./hermes.svg";
import droid from "./droid.svg";
import pi from "./pi.svg";
import cline from "./cline.svg";
import copilot from "./copilot.svg";
import omp from "./omp.svg";
import deepseekHarness from "./deepseek-harness.svg";
import poolside from "./poolside.svg";
import qwen from "./qwen.svg";
import terminal from "./terminal.svg";

export type BrandAsset = { src: string; label: string; kind: "official" | "licensed" | "fallback" };
export const brandAssets: Record<ConnectionClientId, BrandAsset> = {
  claude: { src: claude, label: "Claude Code", kind: "official" },
  codex: { src: codex, label: "Codex CLI", kind: "official" },
  openclaw: { src: openclaw, label: "OpenClaw", kind: "official" },
  opencode: { src: opencode, label: "OpenCode", kind: "official" },
  hermes: { src: hermes, label: "Hermes Agent", kind: "official" },
  "hermes-desktop": { src: hermes, label: "Hermes Desktop", kind: "official" },
  droid: { src: droid, label: "Droid", kind: "official" },
  pi: { src: pi, label: "Pi", kind: "official" },
  cline: { src: cline, label: "Cline", kind: "official" },
  copilot: { src: copilot, label: "Copilot CLI", kind: "official" },
  omp: { src: omp, label: "Oh My Pi", kind: "official" },
  dsh: { src: deepseekHarness, label: "DeepSeek Harness", kind: "official" },
  pool: { src: poolside, label: "Poolside", kind: "official" },
  qwen: { src: qwen, label: "Qwen Code", kind: "official" },
  terminal: { src: terminal, label: "Terminal", kind: "fallback" },
};
export const ollamaBrandAsset: BrandAsset = { src: ollama, label: "Ollama", kind: "official" };
```

Importar cada SVG com a resolução de assets do Vite. O `Record` deve impedir omissão ou id incorreto.

- [ ] **Step 4: Verificar os assets**

```bash
find frontend/src/assets/brands -name '*.svg' -print -exec file {} \;
cd frontend && npm run typecheck
```

Esperado: todos os arquivos listados, SVGs reconhecidos e typecheck PASS.

- [ ] **Step 5: Commitar**

```bash
git add frontend/src/assets/brands docs/assets/connection-icons.md
git commit -m "feat: add local connection brand assets"
```

---

### Task 4: Integrar logo e marcas nos componentes

**Files:**
- Modify: `frontend/src/features/shell/OllamaLogo.tsx`
- Modify: `frontend/src/features/connections/ConnectionIcon.tsx`
- Modify: `frontend/src/styles/app.css`
- Test: `frontend/src/features/shell/appShell.test.tsx`
- Test: `frontend/src/features/connections/connections.test.tsx`

**Interfaces:**
- Consumes: `brandAssets` e `ollamaBrandAsset` da Task 3.
- Produces: imagens locais decorativas, identificadas por `data-brand-icon` e `data-ollama-brand`.

- [ ] **Step 1: Escrever testes que falham**

Verificar que os 15 cards possuem `[data-brand-icon]` e que o link da marca possui `[data-ollama-brand]`. Manter os testes existentes de seleção e clipboard.

- [ ] **Step 2: Confirmar a falha**

```bash
cd frontend && npm test -- --run src/features/shell/appShell.test.tsx src/features/connections/connections.test.tsx
```

Esperado: FAIL porque os componentes ainda usam os SVGs genéricos.

- [ ] **Step 3: Implementar `ConnectionIcon` pelo mapa**

```tsx
export function ConnectionIcon({ id, className = "" }: Props) {
  const asset = brandAssets[id];
  return <img className={`connection-icon ${className}`} src={asset.src} alt="" aria-hidden="true" data-brand-icon={id} />;
}
```

Remover o `switch` de desenhos inline, mas manter a mesma API pública e os mesmos ids.

- [ ] **Step 4: Usar o logo local do Ollama**

```tsx
export function OllamaLogo() {
  return <img className="ollama-logo" src={ollamaBrandAsset.src} alt="" aria-hidden="true" data-ollama-brand />;
}
```

Manter o texto “Ollama Configurator” e o link para Modelos.

- [ ] **Step 5: Ajustar somente o tratamento visual**

```css
.connection-card-mark { display: grid; place-items: center; width: 44px; height: 44px; flex: 0 0 auto; border-radius: 12px; background: var(--surface-subtle); }
.connection-icon { display: block; width: 28px; height: 28px; object-fit: contain; }
.connection-card.is-selected .connection-card-mark { background: var(--surface-subtle); }
.ollama-logo { display: block; width: 22px; height: 22px; object-fit: contain; }
```

Não recolorir automaticamente as marcas; seleção continua sendo comunicada pelo card e pelo texto.

- [ ] **Step 6: Verificar e commitar**

```bash
cd frontend && npm test -- --run src/features/shell/appShell.test.tsx src/features/connections/connections.test.tsx
cd frontend && npm run typecheck
git add frontend/src/features/shell/OllamaLogo.tsx frontend/src/features/connections/ConnectionIcon.tsx frontend/src/styles/app.css frontend/src/features/shell/appShell.test.tsx frontend/src/features/connections/connections.test.tsx
git commit -m "feat: use local brand icons in configurator"
```

Esperado: testes e typecheck PASS.

---

### Task 5: QA funcional, visual e de acessibilidade

**Files:**
- Create: `.impeccable/review/desktop.png`
- Create: `.impeccable/review/mobile.png`
- Modify: `docs/assets/connection-icons.md` somente se a verificação de origem/licença encontrar erro.

**Interfaces:**
- Consumes: componentes e assets das Tasks 1–4.
- Produces: evidência de layout, comportamento, build e acessibilidade.

- [ ] **Step 1: Rodar a suíte completa**

```bash
cd frontend && npm test -- --run
cd frontend && npm run typecheck
cd frontend && npm run build
```

Esperado: PASS nos três comandos.

- [ ] **Step 2: Fazer inspeção desktop**

Com o launcher existente, sem iniciar uma segunda instância, abrir `http://127.0.0.1:5173/#models` e verificar: rolagem da direita mantém marca/menu/gateway; rolagem do menu não move a direita; os quatro links navegam; claro/escuro mantém contraste; Terminal e OpenCode continuam copiando; recarregar não causa tela vazia ou piscadas.

- [ ] **Step 3: Fazer inspeção mobile e teclado**

Em 390px e na viewport real do usuário, verificar ausência de overflow horizontal, marca visível, navegação horizontal alcançável, conteúdo acessível e foco visível em marca, links, selects e cards.

- [ ] **Step 4: Rodar o detector mecânico uma única vez**

```bash
/Users/mac/.agents/skills/impeccable/scripts/impeccable detect --json frontend/src/features/shell/AppShell.tsx frontend/src/features/shell/OllamaLogo.tsx frontend/src/features/connections/ConnectionIcon.tsx frontend/src/styles/app.css
```

Corrigir somente achados mecânicos introduzidos nesta etapa; registrar os pré-existentes sem ampliar o escopo.

- [ ] **Step 5: Revisar escopo e commitar QA**

```bash
git diff --stat ae47809..HEAD
git status --short
git diff --check
# Se houver arquivos desta etapa já modificados antes do trabalho, usar git add -p.
# As capturas em .impeccable/review são evidência local e não entram no commit.
# Se a QA não exigir correção, não criar commit vazio.
git add -p docs/assets/connection-icons.md frontend/src/features/shell frontend/src/features/connections frontend/src/styles/app.css
git commit -m "test: verify shell and brand icon redesign"
```

Confirmar que nenhum backend, gateway, persistência ou instalador foi incluído.
