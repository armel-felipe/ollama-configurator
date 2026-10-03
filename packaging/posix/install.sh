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

# macOS applies a quarantine attribute to files extracted from downloaded ZIPs.
# PyInstaller's embedded Python is then rejected as a nested library by the
# system policy, even though the arm64 executable itself is valid. The user
# has explicitly launched this installer, so clear only the download marker
# from the installed application. Linux has no xattr dependency here.
if [[ "$(uname -s)" == "Darwin" ]] && command -v xattr >/dev/null 2>&1; then
  xattr -dr com.apple.quarantine "$INSTALL_DIR" 2>/dev/null || true
fi

printf 'Ollama Configurator instalado em %s\n' "$INSTALL_DIR"
