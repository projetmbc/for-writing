#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent.parent

sys.path.append(str(BUILD_TOOLS_DIR))


from cbutils.core   import *
from cbutils.texnco import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil import rmtree


# TODO
