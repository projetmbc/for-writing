#!/usr/bin/env python3

import re

import                   logging
from rich.logging import RichHandler
from rich.console import Console


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

LOG_FILE = "tools.log"

RICH_FORMAT_PATTERN = re.compile(r'\[.*?\]')

STYLES = {
    logging.WARNING : "dark_goldenrod",
    logging.ERROR   : "bright_red",
    logging.CRITICAL: "black on wheat1",
}


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

LOG_PRINTERS = {
    (TAG_INFO    := "info")    : logging.info,
    (TAG_WARNING := "warning") : logging.warning,
    (TAG_CRITICAL:= "critical"): logging.critical,
    (TAG_ERROR   := "error")   : logging.error,
}


# ---------------- #
# -- FORMATTING -- #
# ---------------- #


###
# For the terminal, we change the colors used depending on the type
# of message (we use the formatting mark-up ''rich'' language).
###
class RichColorFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelno
        msg   = record.getMessage()

        if level in STYLES:
            color      = STYLES[level]
            record.msg = f"[{color}]{msg}[/{color}]"

        return super().format(record)


###
# We customise the log file formatting so that it removes formatting
# mark-up ''rich'' language.
###
class FileFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()

        if isinstance(msg, str):
            record.msg = RICH_FORMAT_PATTERN.sub('', msg)

        formatted_message = super().format(record)
        record.msg        = msg

        return formatted_message


# --------------------- #
# -- LOGGING CONFIG. -- #
# --------------------- #

###
# prototype::
#     no_color : set to ''False'', the log information will be
#                printed in color; otherwise, it will be printed
#                in black and white.
#
#     :action: the function lives up to its name.
###
def setup_logging(no_color: bool = False) -> None:
# Terminal handler
#
# ''color_system = "auto"'' detects whether the output is a real
# terminal. If not—such as when output is redirected via a pipe—no
# color is used.
    console = Console(
        stderr       = True,
        color_system = None if no_color else "auto"
    )

    term_handler = RichHandler(
        console         = console,
        rich_tracebacks = True,
        markup          = True
    )

    term_handler.setLevel(logging.INFO)
    term_handler.setFormatter(
        RichColorFormatter("%(message)s")
    )

# File handler.
    file_handler = logging.FileHandler(LOG_FILE, mode = "a")

    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(
        FileFormatter("%(asctime)s [%(levelname)s] %(message)s")
    )

# Apply our config.
    logging.basicConfig(
# We need to reset the config.
        force    = True,
        level    = logging.INFO,
        handlers = [term_handler, file_handler],
    )


###
# Let's activate our configurations.
###
setup_logging()
