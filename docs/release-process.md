# Processo de release

1. Atualizar a versão em `backend/config.py` e `frontend/package.json`.
2. Rodar a suíte completa local, incluindo `tests/packaging`.
3. Criar uma tag `vX.Y.Z` e deixar os workflows nativos produzirem os
   artefatos macOS e Windows.
4. Gerar checksums dos arquivos publicados:

   ```bash
   shasum -a 256 OllamaConfigurator-* > checksums.txt
   ```

5. Assinar/notarizar os artefatos macOS com Developer ID e assinar o artefato
   Windows com Authenticode antes da publicação.
6. Instalar, atualizar, iniciar e desinstalar em uma máquina limpa de cada
   plataforma. Confirmar que os modelos do Ollama permanecem intactos.
7. Publicar no GitHub Releases somente depois desses checks e anexar os
   artefatos e `checksums.txt`.

O pipeline atual cria bundles reproduzíveis e faz upload dos artefatos. As
credenciais de assinatura e a validação em máquinas limpas são deliberadamente
responsabilidades do ambiente de release, nunca valores gravados no repositório.
