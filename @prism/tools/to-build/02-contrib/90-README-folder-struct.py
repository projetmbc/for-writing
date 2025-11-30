#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

SRC_DIR     = TOOLS_DIR.parent
CONTRIB_DIR = SRC_DIR / "contrib"


TMPL_TAG_STRUCT = "<!-- FOLDER STRUCT. AUTO - {} -->"

TAG_STRUCT_START = TMPL_TAG_STRUCT.format("START")
TAG_STRUCT_END   = TMPL_TAG_STRUCT.format("END")


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
