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

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PRODS_DIR        = PROJ_DIR / "contrib" / "products"
CONTRIB_PRODS_README_DIR = CONTRIB_PRODS_DIR / "readme"


TMPL_TAG_STRUCT = "<!-- FOLDER STRUCT. AUTO - {} -->"

TAG_STRUCT_START = TMPL_TAG_STRUCT.format("START")
TAG_STRUCT_END   = TMPL_TAG_STRUCT.format("END")


TAB_DIR = '\n  + '


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

_folders = [
    p.name
    for p in CONTRIB_PRODS_DIR.glob('*')
    if (
        p.is_dir()
        and
        not p.name.startswith('x-')
        and
        (
            p.name.startswith('template-')
            or
            not (p / "extend.py").is_file()
        )
    )
]

_folders.sort()

if _folders:
    _folders.append('[...]')

    folders = TAB_DIR.join(_folders)
    folders = f"{TAB_DIR}{folders}"

else:
    folders = ""


subcontent = f"+ {CONTRIB_PRODS_DIR.name}{folders}"
subcontent = f"""
~~~
{subcontent}
~~~
""".strip()


for mdfile in CONTRIB_PRODS_README_DIR.rglob("*.md"):
    tag_update(
        logger          = logging,
        log_raise_error = log_raise_error,
        txtfile         = mdfile,
        tag_start       = TAG_STRUCT_START,
        tag_end         = TAG_STRUCT_END,
        subcontent      = subcontent,
        error_about     = {
            TAG_CONTEXT  : "README - CONTRIBS - Folder structure",
            TAG_FILE_PATH: f"{mdfile.relative_to(PROJ_DIR)}",
        },
    )
