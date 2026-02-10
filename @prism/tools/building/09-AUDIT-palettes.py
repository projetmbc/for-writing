#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TEX_ONE_PAL_TMP = r"""
\documentclass{article}

\usepackage{nicematrix}
\usepackage{amssymb}


\begin{document}

\textbf{\texttt{A}}

\smallskip
\hspace{2pt}\begin{NiceTabular}{*{5}{w{l}{2cm}}}[baseline=1]
    Orangegrey
        & $\square$ colorblind &  $\boxtimes$ cyclic & $\square$ dark & $\square$ divergent \\
        & $\boxtimes$ qualitative & $\square$ semantic &  $\boxtimes$ sequential \\
\end{NiceTabular}

\hspace{2pt}\begin{NiceTabular}{*{5}{w{l}{1.8cm}}}[baseline=1]
    Orangegrey
        & $\square$ colorblind &  $\boxtimes$ cyclic & $\square$ dark & $\square$ divergent \\
        & $\boxtimes$ qualitative & $\square$ semantic &  $\boxtimes$ sequential \\
\end{NiceTabular}

\end{document}
"""


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE    = AUDIT_DIR / "palettes.db"
TEX_NEW_PALS_FILE = AUDIT_DIR / "NEW-PALS.tex"


ALL_CATEGOS = list(
    sorted(
        YAML_CONFIGS['METADATA']['CATEGORY']
    )
)


# ------------------ #
# -- GET LAST NEW -- #
# ------------------ #

logging.warning("LAST NEW PALS NOT YET IMPLEMENTED!")


# --------------------------- #
# -- DB - EXTRACT METADATA -- #
# --------------------------- #

logging.info("DB - Extract 'metadata'")

query = '''
SELECT
    COALESCE(a.alias, h.name),
    h.kind
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
'''

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(query)

    for name, kinds in cursor.fetchall():
        _kinds = set(
            k.strip()
            for k in kinds.split(',')
        )
