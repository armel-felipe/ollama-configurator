#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(uname -s)" == "Darwin" ]]; then
  INSTALL_DIR="$HOME/Library/Application Support/Ollama Configurator"
else
  INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/Ollama Configurator"
fi

mkdir -p "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/backend" "$INSTALL_DIR/frontend"
cp -R "$SCRIPT_DIR/backend" "$INSTALL_DIR/backend"
cp -R "$SCRIPT_DIR/frontend" "$INSTALL_DIR/frontend"
printf 'Ollama Configurator instalado em %s\n' "$INSTALL_DIR"
