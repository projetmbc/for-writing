#!/bin/bash

# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR="$(cd "$(dirname "$0")" && pwd)"

THIS_NAME=$(basename "$0")
THIS_STEM=${THIS_NAME%%.*}


# ------------ #
# -- MANUAL -- #
# ------------ #

USAGE="Usage: bash $THIS_NAME [OPTIONS]"
TRY="'bash $THIS_NAME --help' for help."

HELP="$USAGE

  Launch all project tools (coded in Python).

Options:
  -q, --quick Any builder named '...-slow.py' will be ignored.
              This option is useful during the development phase,
              but NOT WHEN THE PROJECT HAS TO BE PUBLISHED.
  -h, --help  Show this message and exit.
"


# ----------- #
# -- TOOLS -- #
# ----------- #

###
# prototype::
#     #1 : an error code.
#     #2 : a message.
###
print_cli_info() {
    echo "$2"
    exit $1
}


###
# prototype::
#     #1 : a directory path.
#     #2 : a file name.
###
error_exit() {
    printf "\033[91m\033[1m"

    echo "  ERROR , see the file:"
    echo "    + $1/$2"

    exit 1
}


###
# prototype::
#     #1 : a terminal colour code.
#     #2 : a message.
###
print_about() {
    printf "\033[$1"
    echo "$2"
    printf "\033[0m"
}


# ------------------- #
# -- ACTION WANTED -- #
# ------------------- #

if (( $# > 1 ))
then
    message="$USAGE
$TRY

Error: Too much options."

    print_cli_info 1 "$message"
fi


QUICKOPTION=0

if (( $# == 1 ))
then
    case $1 in
        "-q"|"--quick")
            QUICKOPTION=1
        ;;

        "-h"|"--help")
            print_cli_info 0 "$HELP"
        ;;

        *)
            message="$USAGE
$TRY

Error: No such option: $1"

            print_cli_info 1 "$message"
        ;;
    esac
fi


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

# Let's work locally.
cd "$THIS_DIR"

# Logging must be done in the `tools.log` file, and we erase it
# at each launching.
rm -f tools.log

# We ignore any Python file inside the `cbutils` folder.
find . -type f -name "*.py" ! -path "./cbutils/*" | sort | while read -r builderfile
do
    echo ""

    filename=$(basename "$builderfile")

    if [[ $QUICKOPTION == 1 && $filename =~ ^.*-slow\.py ]]
    then
# Yellow formatting.
        print_about "33m" "Ignoring $builderfile"

    else
# Green formatting.
        print_about "32m" "Launching $builderfile"

        python "$builderfile" || error_exit "$THIS_DIR" "$builderfile"
    fi
done

echo ""
