# Processo de release

1. Atualizar somente o arquivo `VERSION`; os manifests, a UI e os artefatos
   devem consumir essa mesma versão.
2. Preparar o ambiente de empacotamento com `uv sync --locked --all-groups`.
   O PyInstaller deve ser executado pelo mesmo Python do projeto; não instalar
   PyInstaller em um Python global diferente do usado por `uv run`.
3. Rodar a suíte completa local, incluindo `tests/packaging`.
4. Criar uma tag `vX.Y.Z` e deixar os workflows nativos produzirem os
   artefatos macOS, Linux e Windows.
5. Gerar checksums dos arquivos publicados:

   ```bash
   shasum -a 256 OllamaConfigurator-* > checksums.txt
   ```

6. Assinar o executável macOS com Developer ID quando a distribuição exigir
   assinatura; o release público usa ZIP e não publica DMG.
7. Instalar, atualizar, iniciar e desinstalar em uma máquina limpa de cada
   plataforma. Confirmar que os modelos do Ollama permanecem intactos.
8. Publicar no GitHub Releases somente depois desses checks e anexar os
   artefatos e `checksums.txt`.

O pipeline atual cria bundles reproduzíveis, faz upload dos artefatos, gera
checksums e publica os ZIPs macOS, Linux e Windows como assets da GitHub
Release associada à tag.

Como smoke test mínimo de macOS/Linux, extrair o ZIP, executar `./install.sh`
e `./run.sh`, e verificar `/api/health`; o processo deve responder antes de
qualquer teste visual no navegador.

As credenciais de assinatura e a validação em máquinas limpas são deliberadamente
responsabilidades do ambiente de release, nunca valores gravados no repositório.
