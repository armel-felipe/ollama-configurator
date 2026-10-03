#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" == "Darwin" ]]; then
  INSTALL_DIR="$HOME/Library/Application Support/Ollama Configurator"
else
  INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/Ollama Configurator"
fi

if [[ -d "$INSTALL_DIR" ]]; then
  rm -rf "$INSTALL_DIR"
fi
printf 'Ollama Configurator removido. As configurações e modelos do Ollama não foram alterados.\n'
