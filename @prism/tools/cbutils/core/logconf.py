#!/usr/bin/env python3

import re

import                   logging
from rich.logging import RichHandler
from rich.console import Console


# --------------- #
# -- CONSTANTS -- #
# --------------- #

LOG_FILE = "tools.log"

RICH_FORMAT_PATTERN = re.compile(r'\[.*?\]')

FSTR_NO_CHANGE      = "{}"
FSTR_COLOR_WARNING  = "[dark_goldenrod]{}[/dark_goldenrod]"
FSTR_COLOR_CRITICAL = "[black on wheat1]{}[/black on wheat1]"
FSTR_COLOR_ERROR    = "[bright_red]{}[/bright_red]"

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
# For the terminal, we change the colours used depending on the type
# of message (we use the formatting mark-up ''rich'' language).
###
class ColorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        levelno = record.levelno

        if levelno >= logging.CRITICAL:
            format_str = FSTR_COLOR_CRITICAL

        elif levelno >= logging.ERROR:
            format_str = FSTR_COLOR_ERROR

        elif levelno >= logging.WARNING:
            format_str = FSTR_COLOR_WARNING

        else:
            format_str = FSTR_NO_CHANGE

        record.msg = format_str.format(record.msg)

        return True


###
# We customise the log file formatting so that it removes formatting
# mark-up ''rich'' language.
###
class FileFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original_message = record.getMessage()
        cleaned_message  = RICH_FORMAT_PATTERN.sub('', original_message)

        record.msg        = cleaned_message
        formatted_message = super().format(record)
        record.msg        = original_message

        return formatted_message


# --------------------- #
# -- LOGGING CONFIG. -- #
# --------------------- #

###
# prototype::
#     no_color  : set to ''False'', the log information will be
#                 printed in color; otherwise, it will be printed
#                 in black and white.
#
#     :action: the function lives up to its name...
###
def setup_logging(no_color: bool = False) -> None:
# Terminal handler
#
# ''color_system = "auto"'' detects whether the output is a real
# terminal. If not—such as when output is redirected via a pipe—no
# color is used
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
    term_handler.addFilter(ColorFilter())

# File handler
    file_handler = logging.FileHandler(
        LOG_FILE,
        mode = "a"
    )
    file_handler.setLevel(logging.ERROR)

    file_formatter = FileFormatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    file_handler.setFormatter(file_formatter)

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
