#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PRODS_DIR = PROJ_DIR / "contrib" / "products"
EXTEND_MDFILE     = (
    CONTRIB_PRODS_DIR / "readme" / "how-to" / "extend.md"
)

FAKE_EXTEND_PYFILE = CONTRIB_PRODS_DIR / "template-stucture" / "extend.py"


TMPL_TAG_STRUCT = "<!-- EXTEND.PY AUTO - {} -->"

TAG_STRUCT_START = TMPL_TAG_STRUCT.format("START")
TAG_STRUCT_END   = TMPL_TAG_STRUCT.format("END")


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

subcontent = FAKE_EXTEND_PYFILE.read_text()
subcontent = f"""
~~~python
{subcontent.strip()}
~~~
""".strip()


tag_update(
    logger          = logging,
    log_raise_error = log_raise_error,
    txtfile         = EXTEND_MDFILE,
    tag_start       = TAG_STRUCT_START,
    tag_end         = TAG_STRUCT_END,
    subcontent      = subcontent,
    error_about     = {
        TAG_CONTEXT  : "README - CONTRIBS - fake 'extend.py' in 'extend.md'",
        TAG_FILE_PATH: f"{EXTEND_MDFILE.relative_to(PROJ_DIR)}",
    },
)
