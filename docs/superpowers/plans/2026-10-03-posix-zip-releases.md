# macOS/Linux ZIP Releases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Publicar releases com ZIP nativo para macOS e Linux, scripts de terminal POSIX compartilhados entre os dois sistemas, manter o pacote Windows com `.bat`/PowerShell e aposentar somente o DMG.

**Architecture:** O backend será compilado nativamente em runners macOS arm64 e Linux x86_64. Ambos os ZIPs POSIX terão a mesma interface (`install.sh`, `run.sh`, `uninstall.sh`) e README bilíngue; o script resolve o diretório de instalação e inicia o backend congelado com o frontend empacotado. O workflow Windows permanece independente e inalterado, exceto pela versão da release.

**Tech Stack:** Bash POSIX, PyInstaller, GitHub Actions, ZIP, FastAPI/React já existentes.

**Spec:** Requisito do usuário nesta conversa: manter Windows `.bat`; remover somente `.dmg`; adicionar pacotes ZIP macOS/Linux com comandos de terminal iguais.

## Global Constraints

- macOS: Apple Silicon arm64.
- Linux: x86_64.
- macOS/Linux usam os mesmos scripts `.sh` e os mesmos comandos.
- Windows continua com `install.bat`, `run.bat`, `uninstall.bat` e scripts PowerShell.
- Nenhum workflow deve publicar DMG.
- Configurações do usuário permanecem fora do diretório instalado e não são removidas pelo `uninstall.sh`.
- A release deve declarar uma nova versão em todos os manifests e READMEs.

## Review Focus

- Executar `run.sh` a partir de qualquer diretório: usar o diretório do próprio script, não o diretório atual.
- Instalação repetida: substituir somente o payload instalado sem apagar configuração persistente.
- macOS sem `xdg-open` e Linux sem `open`: o backend continua abrindo o navegador via `webbrowser`.
- Caminhos com espaços: todos os caminhos dos scripts devem ser citados.
- ZIP POSIX não deve conter `.app`, `.dmg`, `.bat` ou scripts PowerShell.

### Task 1: POSIX launcher scripts and package builder

**Files:**
- Create: `packaging/posix/install.sh`
- Create: `packaging/posix/run.sh`
- Create: `packaging/posix/uninstall.sh`
- Create: `packaging/posix/build-installer.sh`
- Create: `packaging/posix/README-release.md`
- Test: `tests/packaging/test_packaging_smoke.py`

- [ ] Write tests asserting the three scripts use their own directory, preserve the platform-independent command interface, and that the builder includes them in the ZIP.
- [ ] Run the focused packaging tests and verify they fail because the POSIX package files do not exist.
- [ ] Implement scripts using `~/.local/share/Ollama Configurator` on Linux and `~/Library/Application Support/Ollama Configurator` on macOS, with `run.sh` setting `OLLAMA_CONFIGURATOR_FRONTEND_DIR` and `OLLAMA_CONFIGURATOR_OPEN_BROWSER=1`.
- [ ] Implement the builder to invoke the existing backend/frontend builders, copy the payload and scripts, and create `OllamaConfigurator-<platform>-<arch>.zip` without DMG generation.
- [ ] Run focused tests and verify they pass.

### Task 2: Native macOS/Linux workflows

**Files:**
- Modify: `.github/workflows/build-macos.yml`
- Create: `.github/workflows/build-linux.yml`
- Test: `tests/packaging/test_packaging_smoke.py`

- [ ] Update macOS verification and publication to expect only the ZIP and POSIX scripts; remove DMG/checksum references.
- [ ] Add a Linux x86_64 workflow using `ubuntu-latest`, native PyInstaller, ZIP verification, checksum generation, and tag publication.
- [ ] Run YAML/static packaging assertions and inspect workflow asset names.

### Task 3: Release documentation and version

**Files:**
- Modify: `packaging/macos/README-release.md`
- Modify: `packaging/macos/README.md`
- Modify: `docs/packaging.md`
- Modify: `docs/release-process.md`
- Modify: `tests/unit/test_version.py`
- Modify: version manifests and UI version expectations

- [ ] Update both language sections with the shared POSIX command sequence and remove DMG instructions.
- [ ] Bump the application version to `0.1.16` and update all package/test expectations.
- [ ] Run the full backend suite, frontend suite/build, and packaging smoke tests.

### Task 4: Publish and verify release

- [ ] Commit and push `main` plus annotated tag `v0.1.16`.
- [ ] Dispatch macOS, Linux, and Windows package workflows for the tag.
- [ ] Verify the release contains macOS ZIP, Linux ZIP, Windows ZIP, and checksums, with no DMG.
- [ ] Verify the worktree is clean and synchronized with `origin/main`.
