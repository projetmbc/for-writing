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

from natsort import natsorted, ns


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TAG_FOREACH = r"FOREACH CATEGOS"

TAG_FOREACH_START = rf"% -- {TAG_FOREACH} - AUTO - START -- %"
TAG_FOREACH_END   = rf"% -- {TAG_FOREACH} - AUTO - END -- %"


TAB_1 = ' '*4
TAB_2 = TAB_1*2


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate"


SHOWCASE_DIR = TRANSLATE_DIR / "common" / "showcase"

CATEGO_DIR = SHOWCASE_DIR.parent / "categos"
CATEGO_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


MANUAL_DIR        = TRANSLATE_DIR / "en" / "manual"
USED_BY_TOOLS_DIR = TRANSLATE_DIR / "en" / "used-by-tools"


APPENDIX_TEX_FILE = MANUAL_DIR / "appendixes" / "categos.tex"


METADATA_CATEGOS = YAML_CONFIGS['METADATA']['CATEGORY']

CATEGOS = defaultdict(list)


# ------------------ #
# -- DB - CATEGOS -- #
# ------------------ #

with sqlite3.connect(AUDIT_DIR / 'palettes.db') as conn:
    cursor = conn.cursor()

    query = """
SELECT
    h.name, a.alias, h.kind
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for name, alias, kinds in rows:
        if not alias is None:
            name = alias

        for k in kinds.split(','):
            k = k.strip()

            CATEGOS[k].append(name)

for k in CATEGOS:
    CATEGOS[k].sort(key = lambda k: k.lower())


# --------------------------- #
# -- SHOWCASE SINGLE FILES -- #
# --------------------------- #

logging.info("Build 'category showcase' TeX files")

_foreach_data = []

for i, kind in enumerate(
    natsorted(
        CATEGOS,
        alg = ns.IGNORECASE
    ),
    1
):
    logging.info(f"(showcase) '{kind}'")

    texfile = CATEGO_DIR / f"{kind}.latex"
    texfile.touch()

    title = METADATA_CATEGOS[kind]['title']

    _foreach_data.append(
        f"  {i}/{kind}/{{{title}}}"
    )

    _graphics = []

    for n in natsorted(
        set(CATEGOS[kind]),
        alg = ns.IGNORECASE
    ):
        if kind in [
            'qualitative',
            'semantic',
        ]:
            graph_format = 'palette'

        else:
            graph_format = 'spectrum'

        if graph_format == 'palette':
            _graphics += [
                r"\setlength{\columnseprule}{0.5pt}",
                r"\renewcommand{\columnseprulecolor}{\color{LightGrey}}",
            ]

        _graphics += [
             r"\begin{minipage}{\linewidth}",
            rf"{TAB_1}\begin{{center}}",
            rf"{TAB_2}\smallskip",
            rf"{TAB_2}{{\bfseries {n}\vphantom{{g}}}}",
              "",
            rf"{TAB_2}\smallskip",
        ]

        pdffile = SHOWCASE_DIR / f"{n}-{graph_format}.pdf"

        _graphics.append(
            rf'{TAB_2}\includegraphics{{../../../common/showcase/{pdffile.name}}}'
        )

        _graphics += [
            rf"{TAB_1}\end{{center}}",
            r"\end{minipage}",
            "",
        ]

    graphics = '\n'.join(_graphics)

    texfile.write_text(graphics)


# ----------------------- #
# -- DESC SINGLE FILES -- #
# ----------------------- #

logging.info("Build 'category desc' TeX files")

for kind in sorted(CATEGOS):
    logging.info(f"(desc) '{kind}'")

    desc = METADATA_CATEGOS[kind]['desc']

    texfile = USED_BY_TOOLS_DIR / f"catego-desc-{kind}.latex"
    texfile.touch()

    texfile.write_text(desc)


# ----------------------- #
# -- DESC SINGLE FILES -- #
# ----------------------- #

logging.info("Build 'appendix' TeX file")

foreach_data  = ',%\n'.join(_foreach_data)
foreach_data += '%'

content = APPENDIX_TEX_FILE.read_text()

before, _ , after = content.partition(f"\n{TAG_FOREACH_START}")

_ , _ , after = after.partition(f"{TAG_FOREACH_END}\n")

content = f"""
{before}
{TAG_FOREACH_START}
{foreach_data}
{TAG_FOREACH_END}
{after}
""".strip() + '\n'

APPENDIX_TEX_FILE.write_text(content)
