#!/usr/bin/env bash

# ------------------------------------ #
# -- SAFE MODE: FAIL FAST ON ERRORS -- #
# ------------------------------------ #

set -euo pipefail


# --------------- #
# -- CONSTANTS -- #
# --------------- #

readonly THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly THIS_NAME="$(basename "$0")"
readonly THIS_STEM="${THIS_NAME%%.*}"


# ------------ #
# -- MANUAL -- #
# ------------ #

readonly USAGE="Usage: bash $THIS_NAME [OPTIONS]"
readonly TRY="Try 'bash $THIS_NAME --help' for help."
readonly HELP="$USAGE
  Launch all project tools (coded in Python).

Options:
  -q, --quick  Skip any builder named '...-slow.py' or '...-slow.sh'.
               Useful during development, but NOT for production releases.
  -h, --help   Show this message and exit.
"


# ------------ #
# -- COLORS -- #
# ------------ #

readonly COLOR_RESET='\033[1;0m'

readonly COLOR_SELECTION='\033[1;36m'
readonly COLOR_ERROR='\033[1;31m'
readonly COLOR_EXEC='\033[1;32m'
readonly COLOR_IGNORE='\033[1;33m'


# -------------- #
# -- MESSAGES -- #
# -------------- #

# Print colored message.
print_colored() {
    local color="$1"
    local message="$2"

    echo -e "${color}${message}${COLOR_RESET}"
}

# Print message and exit with given code.
print_cli_info() {
    local exit_code="$1"
    local message="$2"

    if [[ $exit_code -ne 0 ]]; then
        echo "$message" >&2
    else
        echo "$message"
    fi

    exit "$exit_code"
}

# Print a section header with auto-sized separator
print_section() {
    local title="$1"
    local title_with_spaces="-- $title --"
    local length=${#title_with_spaces}
    local separator=$(printf '%*s' "$length" | tr ' ' '-')

    echo -e "$COLOR_SELECTION"
    echo "$separator"
    echo "$title_with_spaces"
    echo "$separator"
    echo -e "$COLOR_RESET"
}


# ------------ #
# -- ERRORS -- #
# ------------ #

# Print error and exit.
error_exit() {
    local file_path="$1"

    print_colored "${COLOR_ERROR}" "ERROR - Command failed:"
    print_colored "${COLOR_ERROR}" "File: $file_path"

    exit 1
}


# --------------- #
# -- EXECUTION -- #
# --------------- #

# Execute file with appropriate interpreter
execute_file() {
    local file="$1"
    local interpreter="$2"
    local quick_mode="$3"
    local filename="$(basename "$file")"

    # Skip slow files in quick mode
    if [[ $quick_mode -eq 1 && $filename =~ -slow\.(py|sh)$ ]]
    then
        print_colored "$COLOR_IGNORE" "- Skipping (slow) '$file'"
        return 0
    fi

    print_colored "$COLOR_EXEC" "+ Executing '$file'"

    # Execute and show output directly
    if ! "$interpreter" "$file"
    then
        error_exit "$file"
    fi
}


# ------------------- #
# -- PARSE OPTIONS -- #
# ------------------- #

quick_mode=0

if [[ $# -gt 1 ]]
then
    print_cli_info 1 "$USAGE
$TRY
Error: Too many options."
fi

if [[ $# -eq 1 ]]; then
    case "$1" in
        -q|--quick)
            quick_mode=1
            ;;
        -h|--help)
            print_cli_info 0 "$HELP"
            ;;
        *)
            print_cli_info 1 "$USAGE
$TRY
Error: Unknown option: $1"
            ;;
    esac
fi


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

cd "$THIS_DIR"

# -- Process Python files -- #

print_section "PYTHON SCRIPTS"

while IFS= read -r -d '' py_file
do
    execute_file "$py_file" "python" "$quick_mode"
done < <(find . -type f -name "*.py" ! -path "./cbutils/*" -print0 | sort -z)

echo ""

# -- Process Shell files -- #

print_section "SHELL SCRIPTS"

while IFS= read -r -d '' sh_file
do
    execute_file "$sh_file" "bash" "$quick_mode"
done < <(find . -type f -name "*.sh" ! -name "$THIS_NAME" -print0 | sort -z)

# -- Nothing left to do -- #

print_colored "$COLOR_EXEC" "[OK] All tools executed successfully."
