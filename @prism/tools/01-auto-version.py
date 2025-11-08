#!/usr/bin/env python3

from pathlib import Path
import              sys

TOOLS_DIR = Path(__file__).parent.parent
sys.path.append(str(TOOLS_DIR))

from cbutils.core import *

from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent

PROJECT_ABOUT_YAML = PROJ_DIR / "about.yaml"
TOOLS_VERSION_TXT  = THIS_DIR / "VERSION.txt"


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Last version number.")

version = safe_load(PROJECT_ABOUT_YAML.read_text())
version = version['project']['version']

TOOLS_VERSION_TXT.touch()
TOOLS_VERSION_TXT.write_text(version)
