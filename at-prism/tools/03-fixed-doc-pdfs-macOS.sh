set -euo pipefail  # Exit on error, undefined variables, and pipe failures.


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

  exit 1
}


# ----------------------- #
# -- COMPILE TEX FILES -- #
# ----------------------- #

readonly TRANSLATE_FOLDER="contrib/translate"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/.."

cd "$PROJECT_ROOT"

while IFS= read -r -d '' tex_file
do
  echo "-- NEW TEX FILE --"
  echo "./$tex_file"

  local_dir="$(dirname "$tex_file")"
  filename="$(basename "$tex_file")"

  # Déterminer le moteur LaTeX
  if head -n 1 "$tex_file" | grep -q '^% *!TEX TS-program *= *lualatex'
  then
    texcmd="lualatex"
  else
    texcmd="pdflatex"
  fi

# Compilation in the good directory.
  (
    cd "$local_dir" || exit 1
    SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 \
      latexmk -quiet -pdf \
      -pdflatex="$texcmd --interaction=nonstopmode --halt-on-error --shell-escape %O %S" \
      "$filename" || nocompile "$filename"
  )

done < <(find "$TRANSLATE_FOLDER" -name '*.tex' -print0 | sort -z)
