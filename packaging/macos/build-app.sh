#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/dist/macos}"
APP="$OUT/Ollama Configurator.app"

mkdir -p "$OUT"
rm -rf "$APP"
uv run python "$ROOT/scripts/build_backend.py" --output "$OUT/backend"
node "$ROOT/scripts/build_frontend.mjs" --output "$OUT/frontend"

mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/backend" "$APP/Contents/Resources/frontend"
cp "$ROOT/packaging/macos/Info.plist" "$APP/Contents/Info.plist"
cp "$ROOT/packaging/macos/OllamaConfigurator" "$APP/Contents/MacOS/OllamaConfigurator"
chmod +x "$APP/Contents/MacOS/OllamaConfigurator"
cp -R "$OUT/backend/OllamaConfiguratorBackend" "$APP/Contents/Resources/backend/"
cp -R "$OUT/frontend/." "$APP/Contents/Resources/frontend/"

PORTABLE="$OUT/portable"
ZIP="$OUT/OllamaConfigurator-macOS-arm64.zip"
rm -rf "$PORTABLE"
mkdir -p "$PORTABLE"
cp -R "$APP" "$PORTABLE/Ollama Configurator.app"
cp "$ROOT/packaging/macos/README-release.md" "$PORTABLE/README.md"
rm -f "$ZIP"
ditto -c -k --sequesterRsrc "$PORTABLE" "$ZIP"

if command -v hdiutil >/dev/null 2>&1; then
  hdiutil create -volname "Ollama Configurator" -srcfolder "$APP" -ov -format UDZO \
    "$OUT/OllamaConfigurator-macOS.dmg" >/dev/null
fi

printf 'macOS bundle staged at %s\n' "$APP"
