# Desinstalação e dados preservados

Desinstalar o configurador remove somente o aplicativo e os dados dele:

- macOS: `~/Library/Application Support/Ollama Configurator`;
- Windows: `%LOCALAPPDATA%\Ollama Configurator`.

Os modelos do Ollama, o aplicativo Ollama e suas configurações nunca são
removidos pelo configurador. O helper seguro permite conferir o alvo antes de
qualquer remoção:

```bash
uv run python scripts/uninstall.py --dry-run
uv run python scripts/uninstall.py --apply
```

O `--apply` só remove o diretório exato de dados do configurador. Em Windows,
o pacote também oferece `uninstall.ps1`; ele aplica a mesma regra ao diretório
de instalação local.
