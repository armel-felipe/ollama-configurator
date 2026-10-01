# macOS release bundle

`build-app.sh` gera o backend com PyInstaller, compila o frontend e monta
`Ollama Configurator.app`. Em um macOS com `hdiutil`, também gera um `.dmg`.

O bundle é local-only por padrão: a API usa `127.0.0.1` e o gateway usa
`11435`. Assinatura Developer ID e notarização são passos obrigatórios do
release público e não devem ser simulados em desenvolvimento.
