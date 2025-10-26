#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
CONTRIB_DIR  = PROJECT_DIR / "contrib" / "products"
PRODUCTS_DIR = PROJECT_DIR / "products"
README_DIR   = PROJECT_DIR / "readme" / "products"

DOC_KEPT = [
    "title",
    "desc",
    "how-to-use",
]


PATTERN_MD_H1 = re.compile(r'^(.+)\n=+\s*$', flags=re.MULTILINE)
PATTERN_MD_H2 = re.compile(r'^(.+\n)-+\s*$', flags=re.MULTILINE)


# ----------- #
# -- TOOLS -- #
# ----------- #

def header_up(content: str) -> str:
    content = PATTERN_MD_H1.sub(r'### \1', content)
    content = PATTERN_MD_H2.sub(r'\n#### \1', content)

    return content


# ----------------------- #
# -- CONTRIB. ACCEPTED -- #
# ----------------------- #

for prod_dir in PRODUCTS_DIR.glob("*"):
    if not prod_dir.is_dir():
        continue

    name = prod_dir.name

    logging.info(f"Add '{name}' main doc.")


    readme_dir = CONTRIB_DIR / name / "readme"
    content    = []

    for part in DOC_KEPT:
        part = readme_dir / f"{part}.md"

        content.append(part.read_text())

    content = '\n'.join(content)
    content = header_up(content)

    final_file = README_DIR / f"{name}.md"
    final_file.write_text(content)
