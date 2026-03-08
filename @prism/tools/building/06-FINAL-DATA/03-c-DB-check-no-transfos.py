#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
# -- DEBUG - OFF -- #

from typing import Iterator


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

SQL_GET_PAL_IDS = """
SELECT
    COALESCE(a.alias, h.name),
    h.name,
    h.source
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1;
"""


# --------------- #
# -- CONSTANTS -- #
# --------------- #

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT
AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT


SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


PAL_COLOR_LISTS = dict()
PAL_COLOR_SETS  = dict()
UID2_ALIAS_KEPT = dict()
CANDIDATES      = dict()


SUBLIST_PALS          = dict()
SHIFTED_PALS          = dict()
REVERSED_SHIFTED_PALS = dict()


# ------------------ #
# -- GET PAL DEFS -- #
# ------------------ #

for p in sorted(REPORT_DIR.glob('*.json')):
    tokeep = True

    for prefix in [
        'AUDIT',
        'CATEGO',
    ]:
        if p.name.startswith(f'{prefix}-'):
            tokeep = False

            break

    if not tokeep:
        continue

    src = p.stem

    logging.info(f"Get '{src}' palettes")

    with p.open('r') as f:
        paldata = json_load(f)

    for name, data in paldata.items():
        uid = get_uid(name, src)
        uid = uid.lower()

        PAL_COLOR_LISTS[uid] = data[TAG_RGB_COLS]

        PAL_COLOR_SETS[uid] = set(
            tuple(rgb)
            for rgb in data[TAG_RGB_COLS]
        )


# ------------------- #
# -- GET PALS KEPT -- #
# ------------------- #

logging.info("Get 'kept palettes'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_PAL_IDS)

    for alias, name, src in cursor.fetchall():
        uid = get_uid(name, src)

        UID2_ALIAS_KEPT[uid] = alias

PAL_UIDS = list(UID2_ALIAS_KEPT)


# ---------------- #
# -- CANDIDATES -- #
# ---------------- #

logging.info("Looking for 'candidate palettes'")

for uid in PAL_UIDS:
    matches = list()

    for subuid in PAL_UIDS:
        if subuid == uid:
            continue

        if PAL_COLOR_SETS[uid] <=  PAL_COLOR_SETS[subuid]:
            matches.append(subuid)

    if matches:
        CANDIDATES[uid] = matches


nb_candidates = len(CANDIDATES)

if nb_candidates == 0:
    logging.info('No candidate')
    exit(0)

else:
    plurial = '' if nb_candidates == 1 else 's'

    logging.info(f"'{nb_candidates} candidate{plurial}' found")


# ---------------------- #
# -- TRANSFO PALETTES -- #
# ---------------------- #

for ctxt, validator, memodict in [
    ('sublist', isublistof, SUBLIST_PALS),
    ('shifted', isshiftof, SHIFTED_PALS),
    ('reversed and shifted', isreversedshiftof, REVERSED_SHIFTED_PALS),
]:
    logging.info(f"Looking for '{ctxt} palettes'")

    for uid_1, candidates in CANDIDATES.items():
        for uid_2 in candidates:
            test, data = validator(
                pal_1 = PAL_COLOR_LISTS[uid_1],
                pal_2 = PAL_COLOR_LISTS[uid_2],
            )

            if not test:
                continue

            if uid_2 in memodict:
                continue

            memodict[uid_1] = (uid_2, data)

    if memodict:
        logging.info(f"'{len(memodict)} {ctxt}' palettes found")

    else:
        logging.info(f"'No {ctxt} palettes' found")






exit(1)
