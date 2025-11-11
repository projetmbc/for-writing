from collections import defaultdict
from pathlib     import Path

import re


THIS_DIR     = Path(__file__).parent
CLUSTERS_DIR = THIS_DIR.parent / "clusters"

HUMAN_DIR = THIS_DIR

while HUMAN_DIR.name != "tools-lab":
    HUMAN_DIR = HUMAN_DIR.parent

HUMAN_DIR = HUMAN_DIR / "human-choices" / "category"


PALNAME_PATTERN = re.compile(r'\d+_(.+)_inertia_0\.\d+\.png')


NEW_TMPL_HEDAER_TEXT = f"""
# ------------------------- #
# -- New Human Selection -- #
# ------------------------- #
""".strip()

category = defaultdict(list)

for img in CLUSTERS_DIR.glob("*/*.png"):
    match   = PALNAME_PATTERN.search(img.name)

    if not match:
        print(img.name)
        exit()

    palname = match.group(1)

    category[img.parent.name].append(palname)


for c in category:
    category[c].sort(key = lambda x: x.lower())


for catego, names in category.items():
    folder = HUMAN_DIR / catego
    folder.mkdir(exist_ok = True)

    newfile = folder / "new.txt"
    newfile.write_text(
        f"""
{NEW_TMPL_HEDAER_TEXT}

{'\n'.join(names)}
        """.strip() + "\n"
    )
