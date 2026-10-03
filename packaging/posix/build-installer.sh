#!/usr/bin/env bash
set -euo pipefail
export COPYFILE_DISABLE=1

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/dist/posix}"
SYSTEM="${PACKAGE_PLATFORM:-$(uname -s)}"
ARCH="${PACKAGE_ARCH:-$(uname -m)}"
if [[ "$SYSTEM" == "Darwin" ]]; then
  PLATFORM="macOS"
  ARCHIVE_ARCH="arm64"
else
  PLATFORM="Linux"
  ARCHIVE_ARCH="x86_64"
fi

PAYLOAD="$OUT/payload"
ZIP="$OUT/OllamaConfigurator-${PLATFORM}-${ARCHIVE_ARCH}.zip"
rm -rf "$OUT"
mkdir -p "$OUT" "$PAYLOAD"

uv run python "$ROOT/scripts/build_backend.py" --output "$OUT/backend"
node "$ROOT/scripts/build_frontend.mjs" --output "$OUT/frontend"
cp -R "$OUT/backend" "$PAYLOAD/backend"
cp -R "$OUT/frontend" "$PAYLOAD/frontend"
cp "$ROOT/packaging/posix/install.sh" "$PAYLOAD/install.sh"
cp "$ROOT/packaging/posix/run.sh" "$PAYLOAD/run.sh"
cp "$ROOT/packaging/posix/uninstall.sh" "$PAYLOAD/uninstall.sh"
cp "$ROOT/packaging/posix/README-release.md" "$PAYLOAD/README.md"
chmod +x "$PAYLOAD"/*.sh
find "$PAYLOAD" \( -name '._*' -o -name '.DS_Store' \) -delete

(cd "$PAYLOAD" && zip -qr "$ZIP" .)
printf 'POSIX portable installer staged at %s\n' "$ZIP"
