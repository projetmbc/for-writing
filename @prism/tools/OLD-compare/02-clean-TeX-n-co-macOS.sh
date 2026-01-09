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


# ------------------------- #
# -- ONLY KEEP PDF FILES -- #
# ------------------------- #

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR/human/check"

while IFS= read -r -d '' file
do
  if [ -f "$file" ]
  then
    ext="${file##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    if [ "$ext" != "pdf" ]
    then
      rm "$file"
    fi
  fi
done < <(find . -type f -print0)


# -------------------------- #
# -- NO MORE SINGLE FILES -- #
# -------------------------- #

cd "$SCRIPT_DIR/human/single"

while IFS= read -r -d '' file
do
  if [ -f "$file" ]
  then
    rm "$file"
  fi
done < <(find . -type f -print0)
