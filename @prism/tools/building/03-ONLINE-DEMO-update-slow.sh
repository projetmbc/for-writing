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

readonly CSS_PROD_DIR="$PROJECT_ROOT/products/css"
readonly ONLINE_DEMO_DIR="$PROJECT_ROOT/../docs/@prism"

readonly VERSION_TXT="$PROJECT_ROOT/tools/building/VERSION.txt"
readonly INDEX_HTML="$PROJECT_ROOT/../docs/index.html"


# ------------------------------ #
# -- VERSION NB IN INDEX FILE -- #
# ------------------------------ #

echo "    - Update version in 'index.html'"

LAST_VERSION=$(cat "$VERSION_TXT" | tr -d '[:space:]')

sed -i "" "s|<span class=\"badge\">.*</span>|<span class=\"badge\">$LAST_VERSION</span>|g" "$INDEX_HTML"


# ----------------------------------- #
# -- CSS SHOWCASE - MIRROR VERSION -- #
# ----------------------------------- #

echo '    - Build/update online demo for @prism'

mkdir -p "$ONLINE_DEMO_DIR"

# --delete: remove files in destination that are no longer present in source
# -a: archive mode (preserves permissions, ownership, and timestamps)
# -q: quiet mode (suppresses non-error output)
rsync -aq --delete --include='/palettes-hf/***' --include='/showcase/***' --exclude='*' "$CSS_PROD_DIR/" "$ONLINE_DEMO_DIR/"
