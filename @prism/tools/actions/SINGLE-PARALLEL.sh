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
  return 1
}

# ----------------------------- #
# -- COMPILE SINGLE TEX FILE -- #
# ----------------------------- #
function compile_tex_file {
  local tex_file="$1"
  local numfile="$2"

  echo "-- NEW TEX FILE #$numfile --"
  echo "./$tex_file"

  local local_dir="$(dirname "$tex_file")"
  local file_name="$(basename "$tex_file")"

  # Determine LaTeX command
  local texcmd="pdflatex"
  if head -n 1 "$tex_file" | grep -q '^% *!TEX TS-program *= *lualatex'; then
    texcmd="lualatex"
  fi

  # Compile
  (
    cd "$local_dir" || exit 1
    SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 \
      latexmk -quiet -pdf \
      -pdflatex="$texcmd --interaction=nonstopmode --halt-on-error --shell-escape %O %S" \
      "$file_name" || nocompile "$file_name"
  )
}

# ----------------------- #
# -- COMPILE TEX FILES -- #
# ----------------------- #
readonly TEX_FOLDERS=("pre-doc/showcase/single")
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/../.."

# *** ADJUST THIS NUMBER FOR MORE PARALLELISM ***
readonly MAX_JOBS=8  # Set to 8, 16, or higher for more parallel jobs

cd "$PROJECT_ROOT"

echo "Bash version: $BASH_VERSION"
echo "Using $MAX_JOBS parallel jobs"
echo ""

# Collect all .tex files
tex_files=()
for folder in "${TEX_FOLDERS[@]}"; do
  while IFS= read -r -d '' tex_file; do
    tex_files+=("$tex_file")
  done < <(find "$folder" -name 'main*.tex' -print0 | sort -z)
done

echo "Found ${#tex_files[@]} files to compile"
echo ""

# Create temp directory for status files
tmp_dir=$(mktemp -d)
trap "rm -rf $tmp_dir" EXIT

# Handle Ctrl+C gracefully
# trap 'echo ""; echo "Interrupted! Killing all jobs..."; kill $(jobs -p) 2>/dev/null; exit 130' INT TERM

# Track running PIDs in a simple array
running_pids=()
numfile=0

for tex_file in "${tex_files[@]}"; do
  numfile=$((numfile + 1))

  # Wait if we've reached max parallel jobs
  while true; do
    # Clean up finished PIDs
    new_pids=()
    if [[ ${#running_pids[@]} -gt 0 ]]; then
      for pid in "${running_pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
          new_pids+=("$pid")
        fi
      done
    fi

    # Update running PIDs
    running_pids=()
    if [[ ${#new_pids[@]} -gt 0 ]]; then
      running_pids=("${new_pids[@]}")
    fi

    # Check if we have room for another job
    if [[ ${#running_pids[@]} -lt $MAX_JOBS ]]; then
      break
    fi

    sleep 0.1
  done

  # Launch compilation in background
  (
    if compile_tex_file "$tex_file" "$numfile"; then
      echo "0" > "$tmp_dir/status_$numfile"
    else
      echo "1" > "$tmp_dir/status_$numfile"
    fi
  ) &

  running_pids+=("$!")
  echo "[Active jobs: ${#running_pids[@]}/$MAX_JOBS]"
done

# Wait for all remaining jobs
echo ""
echo "Waiting for remaining jobs to complete..."
wait

# Check for failures
failed=0
for ((i=1; i<=numfile; i++)); do
  if [[ -f "$tmp_dir/status_$i" ]]; then
    status=$(cat "$tmp_dir/status_$i")
    if [[ $status -ne 0 ]]; then
      failed=$((failed + 1))
    fi
  else
    failed=$((failed + 1))
  fi
done

echo ""
echo "====================================="
if [[ $failed -eq 0 ]]; then
  echo "✓ All ${#tex_files[@]} files compiled successfully!"
else
  echo "✗ ERROR: $failed file(s) failed to compile!"
  exit 1
fi
echo "======================================"
