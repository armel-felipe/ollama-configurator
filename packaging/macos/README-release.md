# Ollama Configurator v0.1.15 — macOS Apple Silicon (arm64)

## Português

Pelo Finder, mova `Ollama Configurator.app` para Aplicativos e abra normalmente. O pacote abre uma janela do Terminal com os logs do servidor e o navegador da aplicação. Pelo Terminal, sem privilégios de administrador:

```bash
mkdir -p "$HOME/Applications"
ditto "Ollama Configurator.app" "$HOME/Applications/Ollama Configurator.app"
open "$HOME/Applications/Ollama Configurator.app"
```

Para executar diretamente da pasta extraída: `open "Ollama Configurator.app"`. O DMG continua disponível como opção gráfica. Este pacote é exclusivo para Apple Silicon.

## English

In Finder, move `Ollama Configurator.app` to Applications and open it normally. The package opens a Terminal window with the server logs and the application browser. From Terminal, without administrator privileges:

```bash
mkdir -p "$HOME/Applications"
ditto "Ollama Configurator.app" "$HOME/Applications/Ollama Configurator.app"
open "$HOME/Applications/Ollama Configurator.app"
```

To run directly from the extracted folder: `open "Ollama Configurator.app"`. The DMG remains available as the graphical option. This package is for Apple Silicon only.
