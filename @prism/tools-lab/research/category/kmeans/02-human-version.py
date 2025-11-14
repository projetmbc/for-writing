#!/usr/bin/env python3

from pathlib import Path

from collections import defaultdict


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
CLUSTERS_DIR = THIS_DIR.parent / "clusters"


HUMAN_DIR = THIS_DIR

while HUMAN_DIR.name != "tools-lab":
    HUMAN_DIR = HUMAN_DIR.parent

HUMAN_DIR = HUMAN_DIR / "human-choices" / "category"

if not HUMAN_DIR.is_dir():
    HUMAN_DIR.mkdir(parents = True)


NEW_FILE_TAG = "new.txt"


NEW_TMPL_HEADER_TEXT = """
# ------------------------- #
# -- New Human Selection -- #
# ------------------------- #

{names}
""".strip()


# ------------------------------ #
# -- EMPTY AUTO-PROCESS DIRS? -- #
# ------------------------------ #

for p in CLUSTERS_DIR.glob("*"):
    if not p.is_dir() or p.name[0] != '_':
        continue

    for sp in p.glob("*.png"):
        raise OSError(
            f"No PNG files allowed in the following folder.\n"
            f"{p}"
        )


# -------------------------------------- #
# -- PNG SELECTION --> NEW TEXT FILES -- #
# -------------------------------------- #

for catego in CLUSTERS_DIR.glob("*"):
    if not catego.is_dir() or catego.name[0] == '_':
        continue

    newfile = HUMAN_DIR / catego.name / NEW_FILE_TAG

    names = [
        p.stem
        for p in catego.glob("*.png")
    ]

    names.sort()

    if not names:
        if newfile.is_file():
            newfile.unlink()

        continue

    names = '\n'.join(names)

    print(f"+ Recording '{catego.name}' folder selection.")

    if not newfile.parent.is_dir():
        newfile.parent.mkdir()

    newfile.write_text(names)
