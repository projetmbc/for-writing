#!/usr/bin/env bash
set -euo pipefail


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

  if head -n 1 "$tex_file" | grep -q '^% *!TEX TS-program *= *lualatex'
  then
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

readonly CATEGO_FOLDER="pre-doc/showcase/catego"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/../.."
readonly MAX_JOBS=8

cd "$PROJECT_ROOT"

echo "Using pure bash with $MAX_JOBS parallel jobs"


# --------------------------------- #
# -- PURE BASH PARALLEL EXECUTION - #
# --------------------------------- #

tex_files=()
while IFS= read -r -d '' file
do
  tex_files+=("$file")
done < <(find "$CATEGO_FOLDER" -name '*.tex' -print0)

if [[ ${#tex_files[@]} -eq 0 ]]
then
  echo "No .tex files found in $CATEGO_FOLDER"
  exit 0
fi

failed_count=0
total_files=${#tex_files[@]}

for tex_file in "${tex_files[@]}"
do
  while [[ $(jobs -r | wc -l) -ge $MAX_JOBS ]]
  do
    sleep 0.1
  done

  (
    if ! compile_tex "$tex_file"
    then
      exit 1
    fi

    file_name="$(basename "$tex_file")"
    file_stem="${file_name%.*}"

    cp -f "$CATEGO_FOLDER/$file_stem.pdf" "products/showcase/$file_stem.pdf"
  ) &
done

for job in $(jobs -p)
do
  if ! wait "$job"
  then
    ((failed_count++))
  fi
done

if [[ $failed_count -gt 0 ]]
then
  echo "ERROR - $failed_count compilation(s) failed!" >&2
  exit 1
fi

echo "All $total_files compilations completed successfully!"
