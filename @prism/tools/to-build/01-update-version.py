#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent

sys.path.append(str(THIS_DIR))

from cbutils.core import *

from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR.parent


PROJECT_ABOUT_YAML = PROJ_DIR / "about.yaml"
TOOLS_VERSION_TXT  = THIS_DIR / "VERSION.txt"


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Look for project version number.")

version = safe_load(PROJECT_ABOUT_YAML.read_text())
version = version['project']['version']


logging.info(
    f"Update '{TOOLS_VERSION_TXT.relative_to(PROJ_DIR)}'."
)

TOOLS_VERSION_TXT.touch()
TOOLS_VERSION_TXT.write_text(version)
