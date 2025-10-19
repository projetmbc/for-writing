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


# -------------------------- #
# -- COMPILE THE TEX FILE -- #
# -------------------------- #

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/.."
readonly SHOWCASE_FILE_NAME="showcase-en"

cd "$PROJECT_ROOT"

tex_file="pre-doc/$SHOWCASE_FILE_NAME.tex"

echo "-- NEW TEX FILE --"
echo "./$tex_file"


local_dir="$(dirname "$tex_file")"
filename="$(basename "$tex_file")"

# Compilation in the good directory.
(
  cd "$local_dir" || exit 1
  SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 \
    latexmk -quiet -pdf \
    -pdflatex="pdflatex --interaction=nonstopmode --halt-on-error --shell-escape %O %S" \
    "$filename" || nocompile "$filename"
)


# ------------------------------ #
# -- COPY PDF IN FINAL FOLDER -- #
# ------------------------------ #

cp -f "pre-doc/$SHOWCASE_FILE_NAME.pdf" "products/$SHOWCASE_FILE_NAME.pdf"
