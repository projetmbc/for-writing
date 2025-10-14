#!/usr/bin/env python3

from pathlib import Path
import              sys

TOOLS_DIR = Path(__file__).parent.parent
sys.path.append(str(TOOLS_DIR))

from cbutils.core import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
SRC_DIR     = THIS_DIR.parent.parent
CONTRIB_DIR = SRC_DIR / "contrib"

TEMPL_TAG_STRUCT = "<!-- FOLDER STRUCT. AUTO - {} -->"

TAG_STRUCT_START = TEMPL_TAG_STRUCT.format("START")
TAG_STRUCT_END   = TEMPL_TAG_STRUCT.format("END")

TAB_STRUCT = '\n  + '


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

for mdfile in CONTRIB_DIR.rglob("*.md"):
    content = mdfile.read_text()

    if not TAG_STRUCT_START in content:
        continue

    logging.info(
        msg_creation_update(
            context = f"'{mdfile.relative_to(SRC_DIR)}' (auto treeview)",
            upper   = False,
        )
    )

# Check initial content!
    for tag in [
        TAG_STRUCT_START,
        TAG_STRUCT_END,
    ]:
        if content.count(tag) != 1:
            raise ValueError(
                f"use the following special comment only once:\n{tag}"
            )

    before, _ , after = content.partition(f"\n{TAG_STRUCT_START}")

    _ , _ , after = after.partition(f"{TAG_STRUCT_END}\n")

# The sorted list of folders.
    pardir = mdfile.parent

    if pardir.name == "readme":
        pardir = pardir.parent

    folders = [
        p.name
        for p in pardir.glob('*')
        if p.is_dir() and not p.name.startswith('x-')
    ]

    folders.sort()

# Content updated.
    if folders:
        folders = TAB_STRUCT.join(folders)
        folders = f"{TAB_STRUCT}{folders}"

    else:
        folders = ""

    content = f"""{before.strip()}

{TAG_STRUCT_START}
~~~
+ {CONTRIB_DIR.name}{folders}
~~~
{TAG_STRUCT_END}
{after.rstrip()}
    """.rstrip() + '\n'

    mdfile.write_text(content)
