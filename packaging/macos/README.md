# macOS release bundle

`packaging/posix/build-installer.sh` gera o backend com PyInstaller, compila o
frontend e monta um ZIP portátil com scripts de terminal. O pacote não gera
DMG.

O bundle é local-only por padrão: a API usa `127.0.0.1` e o gateway usa
`11435`. Assinatura Developer ID e notarização são passos obrigatórios do
release público e não devem ser simulados em desenvolvimento.
