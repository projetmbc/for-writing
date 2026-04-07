#!/usr/bin/env bash

set -euo pipefail  # Exit on error, undefined variables, and pipe failures.


# ------------------- #
# -- NO ARG NEEDED -- #
# ------------------- #

if [[ $# -ne 0 ]]
then
  echo "CRITICAL - Too much arguments!" >&2

  exit 1
fi


# --------------- #
# -- CONSTANTS -- #
# --------------- #

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/../.."

readonly PROD_DIR="$PROJECT_ROOT/products"
readonly CSS_PROD_DIR="$PROD_DIR/css"
readonly ONLINE_DEMO_DIR="$PROJECT_ROOT/../docs/@prism"

readonly VERSION_TXT="$PROJECT_ROOT/tools/building/VERSION.txt"
readonly INDEX_HTML="$PROJECT_ROOT/../docs/index.html"
readonly FORMATS_JS="$ONLINE_DEMO_DIR/showcase/core/formats.js"
readonly GRAPHICS_JS="$ONLINE_DEMO_DIR/showcase/core/graphic.js"

readonly HF_PROD_PATH="../../../@prism/products/"


# ------------------------------ #
# -- VERSION NB IN INDEX FILE -- #
# ------------------------------ #

echo "    - Update version in 'index.html'"

LAST_VERSION=$(cat "$VERSION_TXT" | tr -d '[:space:]')

sed -i "" "s|<span class=\"badge\">.*</span>|<span class=\"badge\">$LAST_VERSION</span>|g" "$INDEX_HTML"


# ----------------------------- #
# -- BUILD FROM CSS SHOWCASE -- #
# ----------------------------- #

echo '    - Build/update online demo for @prism'


# -- SYNC OF FILES -- #

mkdir -p "$ONLINE_DEMO_DIR"

# --delete: remove files in destination that are no longer present in source
# -a: archive mode (preserves permissions, ownership, and timestamps)
# -q: quiet mode (suppresses non-error output)
rsync -aq --delete --include='/showcase/***' --exclude='*' "$CSS_PROD_DIR/" "$ONLINE_DEMO_DIR/"


# -- GOOD PALETTE CSS PATHS -- #

sed -i '' "s|const cssPath = \`../palettes-hf/\${nom}.css\`;|const cssPath = \`$HF_PROD_PATH/css/palettes-hf/\${nom}.css\`;|g" "$GRAPHICS_JS"


# -- FULL LIST OF FORMATS -- #

formats=""

while IFS= read -r -d '' dir; do
  dir_name=$(basename "$dir")

  first_file=$(find "$dir" -maxdepth 2 -type f -print -quit)

  if [[ "$first_file" == *"."* ]]; then
    ext="${first_file##*.}"

    entry="\"$dir_name\": \"$ext\""

    if [[ -n "$formats" ]]; then
      formats+=", "
    fi

    formats+="$entry"
  fi
done < <(find "$PROD_DIR" -maxdepth 1 -mindepth 1 -type d ! -name "json" -print0)

formats_js="const PAL_FORMAT = {$formats};"

# Écriture dans le fichier
echo "$formats_js" > "$FORMATS_JS"


sed -i '' "s|href=\`../palettes-hf/\${nom}.\${ext}\`|href=\`$HF_PROD_PATH/\${folder}/palettes-hf/\${nom}.\${ext}\`|g" "$GRAPHICS_JS"
