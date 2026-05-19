#!/usr/bin/env bash
# Download GloVe 6B 100d vectors required by REFAIR.py.
# Places the file at both models/ folders the project uses.
# Works on macOS and Linux.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

GLOVE_URL="https://nlp.stanford.edu/data/glove.6B.zip"
TARGET_FILES=(
  "$ROOT/models/glove.6B.100d.txt"
  "$ROOT/ReFair-App/refair-server/models/glove.6B.100d.txt"
)

need_download=false
for f in "${TARGET_FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    need_download=true
    break
  fi
done

if [[ "$need_download" == "false" ]]; then
  echo "GloVe already present in both target locations. Nothing to do."
  exit 0
fi

TMPDIR_=$(mktemp -d)
trap 'rm -rf "$TMPDIR_"' EXIT

echo "Downloading GloVe 6B from $GLOVE_URL (~822 MB compressed) ..."
curl -L --fail --progress-bar -o "$TMPDIR_/glove.6B.zip" "$GLOVE_URL"

echo "Extracting glove.6B.100d.txt ..."
unzip -p "$TMPDIR_/glove.6B.zip" glove.6B.100d.txt > "$TMPDIR_/glove.6B.100d.txt"

for f in "${TARGET_FILES[@]}"; do
  mkdir -p "$(dirname "$f")"
  cp "$TMPDIR_/glove.6B.100d.txt" "$f"
  echo "Wrote $f"
done

echo "Done."
