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


CONTRIB_PRODS_DIR   = PROJ_DIR / "contrib" / "products"
LUA_PROD_DIR        = CONTRIB_PRODS_DIR / "lua"
LUA_PROD_README_DIR = CONTRIB_PRODS_DIR / "readme" / "how-to"


TMPL_TAG_STRUCT = "<!-- LUA PROD DIR. AUTO - {} -->"

TAG_STRUCT_START = TMPL_TAG_STRUCT.format("START")
TAG_STRUCT_END   = TMPL_TAG_STRUCT.format("END")


TAB_DIR  = '\n  + '
TAB_FILE = '\n  * '


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

_files = [
    f.name
    for f in LUA_PROD_DIR.glob('*')
    if (
        f.is_file()
        and
        not f.name.startswith('.')
        and
        f.name != 'README.md'
    )
]

_files.sort()

files = TAB_FILE.join(_files)
files = f"{TAB_FILE}{files}"


_folders = [
    p.name
    for p in LUA_PROD_DIR.glob('*')
    if (
        p.is_dir()
        and
        not p.name.startswith('_')
    )
]

_folders.sort()

folders = TAB_DIR.join(_folders)
folders = f"{TAB_DIR}{folders}"


subcontent = f"+ {LUA_PROD_DIR.name}{files}{folders}"
subcontent = f"""
~~~
{subcontent}
~~~
""".strip()


for mdfile in LUA_PROD_README_DIR.rglob("*.md"):
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
