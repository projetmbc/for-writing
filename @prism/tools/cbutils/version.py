#!/usr/bin/env python3

from pathlib import Path


# --------------- #
# -- CONSTANTS -- #
# --------------- #

VERSION = Path(__file__).parent.parent / "VERSION.txt"
VERSION = VERSION.read_text()
VERSION = VERSION.strip()
