#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" == "Darwin" ]]; then
  INSTALL_DIR="$HOME/Library/Application Support/Ollama Configurator"
else
  INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/Ollama Configurator"
fi

BACKEND="$INSTALL_DIR/backend/OllamaConfiguratorBackend/OllamaConfiguratorBackend"
if [[ ! -x "$BACKEND" ]]; then
  printf 'Aplicação não instalada. Execute ./install.sh primeiro.\n' >&2
  exit 1
fi

export OLLAMA_CONFIGURATOR_FRONTEND_DIR="$INSTALL_DIR/frontend"
export OLLAMA_CONFIGURATOR_OPEN_BROWSER=1
exec "$BACKEND"
