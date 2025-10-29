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


# ------------------------------ #
# -- BUILD SHOWCASE TEX FILES -- #
# ------------------------------ #

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR/.."
readonly PRE_DOC="pre-doc/showcase"
readonly SUFFIXES=("dark" "std")
readonly SHOWCASE_BASE_NAME="showcase-en"

cd "$PROJECT_ROOT"

for suffix in "${SUFFIXES[@]}"
do
  file_name="$SHOWCASE_BASE_NAME-$suffix"
  tex_file="$PRE_DOC/$file_name.tex"

  echo "-- NEW TEX FILE --"
  echo "./$tex_file"

  local_dir="$(dirname "$tex_file")"

  (
    cd "$local_dir" || exit 1
    SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 \
      latexmk -quiet -pdf \
      -pdflatex="pdflatex --interaction=nonstopmode --halt-on-error --shell-escape %O %S" \
      "$file_name" || nocompile "$file_name"
  )

  cp -f "$PRE_DOC/$file_name.pdf" "products/$file_name.pdf"
done
