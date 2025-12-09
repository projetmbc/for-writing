#!/usr/bin/env bash

set -euo pipefail

# Fix for GitHub Actions: disable tput colors
export TERM=dumb

# ------------------- #
# -- NO ARG NEEDED -- #
# ------------------- #
if [[ $# -ne 0 ]]
then
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

# ------------------------------ #
# -- BUILD ONE TEX FILE        -- #
# ------------------------------ #
function build_one_file {
  local tex_file="$1"
  local file_num="$2"

  echo "-- NEW TEX FILE #$file_num --"
  echo "./$tex_file"

  local local_dir file_name texcmd
  local_dir="$(dirname "$tex_file")"
  file_name="$(basename "$tex_file")"

  # Detect which TeX engine to use
  if head -n 1 "$tex_file" | grep -q '^% *!TEX TS-program *= *lualatex'
  then
    texcmd="lualatex"
  else
    texcmd="pdflatex"
  fi

  (
    cd "$local_dir" || exit 1

    # Capture full output for debugging
    if ! SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 \
      latexmk -pdf \
      -pdflatex="$texcmd --interaction=nonstopmode --halt-on-error --shell-escape %O %S" \
      "$file_name" 2>&1; then

      echo "========================================" >&2
      echo "COMPILATION FAILED: $file_name" >&2
      echo "========================================" >&2

      # Show last 50 lines of log file if it exists
      log_file="${file_name%.tex}.log"
      if [[ -f "$log_file" ]]; then
        echo "Last 50 lines of $log_file:" >&2
        tail -n 50 "$log_file" >&2
      fi

      nocompile "$file_name"
      exit 1
    fi
  )

  return $?
}

# ----------------------- #
# -- CONFIGURATION      -- #
# ----------------------- #
readonly TEX_FOLDERS=("pre-doc/showcase" "contrib" "products")
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/../.."

# Adjust ulimit for more files
ulimit -n 2048

cd "$PROJECT_ROOT"

# ------------------------------ #
# -- DETECT NUMBER OF CPUS     -- #
# ------------------------------ #
NUM_JOBS=4  # Default fallback

if command -v nproc &>/dev/null; then
  NUM_JOBS=$(nproc)
elif [[ -f /proc/cpuinfo ]]; then
  NUM_JOBS=$(grep -c ^processor /proc/cpuinfo)
elif command -v sysctl &>/dev/null; then
  NUM_JOBS=$(sysctl -n hw.ncpu 2>/dev/null || echo 4)
fi

echo "Building with $NUM_JOBS parallel jobs..."
echo ""

# ------------------------------ #
# -- COLLECT ALL TEX FILES     -- #
# ------------------------------ #
all_tex_files=()

for folder in "${TEX_FOLDERS[@]}"
do
  if [[ ! -d "$folder" ]]; then
    echo "WARNING: Folder not found: $folder" >&2
    continue
  fi

  while IFS= read -r -d '' tex_file
  do
    all_tex_files+=("$tex_file")
  done < <(find "$folder" -name 'main*.tex' -print0 | sort -z)
done

total_files=${#all_tex_files[@]}
echo "Found $total_files TeX files to compile"
echo ""

if (( total_files == 0 )); then
  echo "No TeX files found!"
  exit 0
fi

# ------------------------------ #
# -- PARALLEL COMPILATION      -- #
# ------------------------------ #
pids=()
pid_to_file=()
successful=0
failed=0
failed_files=()
current_file=0

for tex_file in "${all_tex_files[@]}"
do
  current_file=$((current_file + 1))

  # Launch compilation in background
  (
    if build_one_file "$tex_file" "$current_file"; then
      exit 0
    else
      exit 1
    fi
  ) &

  pid=$!
  pids+=($pid)
  pid_to_file[$pid]="$tex_file"

  # Wait when we reach the max number of parallel jobs
  if (( ${#pids[@]} >= NUM_JOBS )); then
    # Wait for all current jobs to finish
    for pid in "${pids[@]}"; do
      if wait "$pid"; then
        ((successful++))
      else
        ((failed++))
        failed_files+=("${pid_to_file[$pid]}")
      fi
    done
    pids=()
  fi
done

# Wait for remaining jobs
for pid in "${pids[@]}"; do
  if wait "$pid"; then
    ((successful++))
  else
    ((failed++))
    failed_files+=("${pid_to_file[$pid]}")
  fi
done

# ------------------------------ #
# -- SUMMARY                   -- #
# ------------------------------ #
echo ""
echo "=========================================="
echo "COMPILATION SUMMARY"
echo "=========================================="
echo "Total files:      $total_files"
echo "Successful:       $successful"
echo "Failed:           $failed"
echo "=========================================="

if (( failed > 0 )); then
  echo "Failed files:"
  for file in "${failed_files[@]}"; do
    echo "  - $file"
  done
  echo "=========================================="
  exit 1
else
  echo "All files compiled successfully!"
  exit 0
fi
