#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_NB_CLUSTERS = re.compile(
    r'(\\newcommand\\nbSimClusters\{)(\d+)(\})'
)


LUA_TMPL_CODE = r"""
% --------------------------------- %
% -- NO TRANSLATION NEEDED HERE! -- %
% --------------------------------- %

\begin{{luacode*}}
PALETTES = {{
  {cluster}
}}

drawSimPals(PALETTES, {cluster_id})
\end{{luacode*}}
    """.strip() + '\n'


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR    = BUILD_TOOLS_DIR / "REPORT"
SIMILAR_DIR   = PROJ_DIR / "contrib" / "translate" / "common" / "similar"
EN_MANUAL_DIR = PROJ_DIR / "contrib" / "translate" / "en" / "manual"


if SIMILAR_DIR.is_dir():
    for p in SIMILAR_DIR.glob("*.luadraw"):
        if p.is_file():
            p.unlink()

else:
    SIMILAR_DIR.mkdir(
        parents  = True,
        exist_ok = True
    )


TEX_CFG_FILE = EN_MANUAL_DIR / "preamble.cfg.sty"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PAL_CLUSTERS_FILE = REPORT_DIR / "PAL-SIMILAR.json"

with PAL_CLUSTERS_FILE.open(mode = "r") as f:
    ALL_CLUSTERS = json_load(f)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Update 'number of similar palette clusters'.")

content = TEX_CFG_FILE.read_text()
content = content.strip()
content = PATTERN_NB_CLUSTERS.sub(
    r'\g<1>' + str(len(ALL_CLUSTERS)) + '}',
    content
)

TEX_CFG_FILE.write_text(content)


logging.info("Build 'similar palette' TeX files.")


for i, cluster in enumerate(ALL_CLUSTERS, 1):
    filename = f"cluster-{i}.luadraw"

    luacode = LUA_TMPL_CODE.format(
        cluster_id = i,
        cluster    = ',\n  '.join(
            repr(n) for n in cluster
        )
    )

    (SIMILAR_DIR / filename).write_text(luacode)
