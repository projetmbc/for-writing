#!/usr/bin/env bash
set -euo pipefail

# ------------------- #
# -- NO ARG NEEDED -- #
# ------------------- #
if [[ $# -ne 0 ]]; then
  echo "CRITICAL - Too much arguments!" >&2
  exit 1
fi

# ----------------------------- #
# -- OPEN BROKEN LATEX FILES -- #
# ----------------------------- #
function nocompile {
  local file="$1"
  echo "ERROR - Compilation failed for: $file" >&2
  xdg-open "$file" 2>/dev/null || open "$file" 2>/dev/null || echo "Cannot open $file"
}

# ----------------------- #
# -- COMPILE TEX FILES -- #
# ----------------------- #
function compile_tex {
  local tex_file="$1"
  echo "-- NEW TEX FILE --"
  echo "./$tex_file"
  local local_dir="$(dirname "$tex_file")"
  local file_name="$(basename "$tex_file")"
  local texcmd="pdflatex"

  if head -n 1 "$tex_file" | grep -q '^% *!TEX TS-program *= *lualatex'; then
    texcmd="lualatex"
  fi

  (
    cd "$local_dir" || exit 1
    SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 \
      latexmk -quiet -pdf \
      -pdflatex="$texcmd --interaction=nonstopmode --halt-on-error --shell-escape %O %S" \
      "$file_name" || { nocompile "$file_name"; exit 1; }
  )
}

export -f compile_tex nocompile

readonly TRANSLATE_FOLDER="contrib/translate"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/../.."
readonly MAX_JOBS=8

cd "$PROJECT_ROOT"

echo "Using pure bash with $MAX_JOBS parallel jobs"

# --------------------------------- #
# -- PURE BASH PARALLEL EXECUTION - #
# --------------------------------- #

# Collect all .tex files (bash 3.x compatible)
tex_files=()
while IFS= read -r -d '' file; do
  tex_files+=("$file")
done < <(find "$TRANSLATE_FOLDER" -path "$TRANSLATE_FOLDER/common" -prune -o -name '*.tex' -print0)

# Check if any files were found
if [[ ${#tex_files[@]} -eq 0 ]]; then
  echo "No .tex files found in $TRANSLATE_FOLDER"
  exit 0
fi

# Track failures and active jobs
failed_count=0
total_files=${#tex_files[@]}

# Process each file
for tex_file in "${tex_files[@]}"; do
  # Wait if we've reached max concurrent jobs
  while [[ $(jobs -r | wc -l) -ge $MAX_JOBS ]]; do
    sleep 0.1
  done

  # Launch compilation in background
  (
    if ! compile_tex "$tex_file"; then
      exit 1
    fi
  ) &
done

# Wait for all jobs and count failures
for job in $(jobs -p); do
  if ! wait "$job"; then
    ((failed_count++))
  fi
done

# Check for failures
if [[ $failed_count -gt 0 ]]; then
  echo "ERROR - $failed_count compilation(s) failed!" >&2
  exit 1
fi
