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

from collections import defaultdict


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TAG_START = "% -- CATEGOS - AUTO - START -- %"
TAG_END   = "% -- CATEGOS - AUTO - END -- %"


TAB = ' '*6


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR    = BUILD_TOOLS_DIR / TAG_AUDIT
SHOWCASE_DIR = PROJ_DIR / "contrib" / "translate" / "common" / "showcase"

CATEGO_DIR = SHOWCASE_DIR.parent / "categos"
CATEGO_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


APPENDIX_TEX_FILE = PROJ_DIR / "contrib" / "translate" / "en" / "manual" / "appendixes" / "categos.tex"


METADATA_CATEGOS = YAML_CONFIGS['METADATA']['CATEGORY']

CATEGOS = defaultdict(list)


# ------------------ #
# -- DB - CATEGOS -- #
# ------------------ #

with sqlite3.connect(AUDIT_DIR / 'palettes.db') as conn:
    cursor = conn.cursor()

    query = """
SELECT
    p.name, p.kind
FROM hash p
WHERE p.is_kept = 1
ORDER BY p.name ASC
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for name, kinds in rows:
        for k in kinds.split(','):
            k = k.strip()

            CATEGOS[k].append(name)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'category' TeX files")

_foreach_data = []

for i, kind in enumerate(sorted(CATEGOS), 1):
    logging.info(f"Add '{kind}'")

    texfile = CATEGO_DIR / f"{kind}.latex"
    texfile.touch()

    title = METADATA_CATEGOS[kind]['title']

    _foreach_data.append(
        f"  {i}/{kind}/{{{title}}}"
    )

    _graphics = []


    for n in CATEGOS[kind]:
        _graphics.append(n)

        if kind in [
            'qualitative',
            'semantic',
        ]:
            format = 'palette'

        else:
            format = 'spectrum'

        pdffile = SHOWCASE_DIR / f"{n}-{format}.pdf"

        if not pdffile.is_file():
            continue


        _graphics.append(
            rf'{TAB}\includegraphics{{../../../common/showcase/{pdffile.name}}}'
        )

    graphics = '\n\n\\smallskip\n'.join(_graphics)

    texfile.write_text(graphics)



logging.info("Build 'appendix' TeX file")

foreach_data  = ',%\n'.join(_foreach_data)
foreach_data += '%'

content = APPENDIX_TEX_FILE.read_text()

before, _ , after = content.partition(f"\n{TAG_START}")

_ , _ , after = after.partition(f"{TAG_END}\n")

content = f"""
{before}
{TAG_START}
{foreach_data}
{TAG_END}
{after}
""".strip() + '\n'

APPENDIX_TEX_FILE.write_text(content)
