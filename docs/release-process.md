# Processo de release

1. Atualizar a versão em `backend/config.py` e `frontend/package.json`.
2. Preparar o ambiente de empacotamento com `uv sync --locked --all-groups`.
   O PyInstaller deve ser executado pelo mesmo Python do projeto; não instalar
   PyInstaller em um Python global diferente do usado por `uv run`.
3. Rodar a suíte completa local, incluindo `tests/packaging`.
4. Criar uma tag `vX.Y.Z` e deixar os workflows nativos produzirem os
   artefatos macOS e Windows.
5. Gerar checksums dos arquivos publicados:

   ```bash
   shasum -a 256 OllamaConfigurator-* > checksums.txt
   ```

6. Assinar/notarizar os artefatos macOS com Developer ID e assinar o artefato
   Windows com Authenticode antes da publicação.
7. Instalar, atualizar, iniciar e desinstalar em uma máquina limpa de cada
   plataforma. Confirmar que os modelos do Ollama permanecem intactos.
8. Publicar no GitHub Releases somente depois desses checks e anexar os
   artefatos e `checksums.txt`.

O pipeline atual cria bundles reproduzíveis, faz upload dos artefatos, gera
checksums e publica o `.dmg` macOS e o pacote Windows como assets da GitHub
Release associada à tag.

Como smoke test mínimo do macOS, executar o launcher do bundle e verificar
`/api/health`; o processo deve responder antes de qualquer teste visual no
navegador. Isso evita publicar um DMG cujo executável congelado inicia mas
encerra por dependência Python ausente.

As credenciais de assinatura e a validação em máquinas limpas são deliberadamente
responsabilidades do ambiente de release, nunca valores gravados no repositório.
