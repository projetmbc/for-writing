#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
# -- DEBUG - OFF -- #

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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_GET_PAL_KEPT = """
SELECT
    h.pal_id, h.name, a.alias
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
"""

SQL_TABLE_INSERT = '''
INSERT INTO alias (
    pal_id,
    alias
) VALUES ({placeholders})
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ----------- #
# -- TOOLS -- #
# ----------- #

def dbadd_aliaspals(
    conn,
    pal_id: int,
    alias : str
) -> None:
    placeholders = ['?']*(len(locals()) - 1)
    placeholders = ','.join(placeholders)

    try:
        cursor = conn.cursor()

        cursor.execute(
            SQL_TABLE_INSERT.format(
                placeholders = placeholders
            ),
            (
                pal_id,
                alias
            )
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "Alias DB.",
            desc      = f"Insertion fails for '{alias}'.",
            exception = Exception,
        )


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

POST_ALIAS_YAML = AUDIT_DIR / 'POST-ALIAS.yaml'
POST_ALIAS_YAML.touch()

with POST_ALIAS_YAML.open(mode = 'r') as f:
    POST_ALIAS = yaml.safe_load(f)


# ---------------- #
# -- POST ALIAS -- #
# ---------------- #

logging.info("Post Alias DB - 'Populate'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_PAL_KEPT)

    for pal_id, name, alias in cursor.fetchall():
        if alias in POST_ALIAS:
            log_raise_error(
                context   = 'Post Alias',
                desc      = f"'{name}' already has an alias",
                exception = ValueError,
            )

        if not name in POST_ALIAS:
            continue

        dbadd_aliaspals(
            conn   = conn,
            pal_id = pal_id,
            alias  = POST_ALIAS[name],
        )
