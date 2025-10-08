# ------------------- #
# -- NO ARG NEEDED -- #
# ------------------- #

if [ ! $# -eq 0 ]
then
  echo "CRITICAL - Too much arguments!"
  exit 1
fi


# ----------------------------- #
# -- OPEN BROKEN LATEX FILES -- #
# ----------------------------- #

function nocompile {
  open "$1"

  exit 1
}


# ----------------------- #
# -- COMPILE TEX FILES -- #
# ----------------------- #

TEX_FOLDERS=("contrib" "products")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR/../"

for folder in "${TEX_FOLDERS[@]}"
do
  for f in $(find "$folder" -name 'main*.tex' | sort -u)
  do
    echo "-- NEW TEX FILE --"
    echo "./$f"

    fdir=$(dirname "$f")
    fname="$(basename "$f")"

    cd "$fdir"

    if head -n 1 "$fname" | grep '^% *!TEX TS-program *= *lualatex'
    then
      texcmd="lualatex"

    else
      texcmd="pdflatex"
    fi

    SOURCE_DATE_EPOCH=0 FORCE_SOURCE_DATE=1 latexmk -quiet -pdf -pdflatex="$texcmd --interaction=nonstopmode --halt-on-error --shell-escape  %O %S" "$SCRIPT_DIR/../$f" || nocompile "$fname"

    cd "$SCRIPT_DIR/../"
  done  # for f in $(find . -name '*.tex')
done    # for folder in "${TEX_FOLDERS[@]}"
