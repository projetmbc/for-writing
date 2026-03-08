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

from yaml import dump as yaml_dump

from natsort import (
    natsorted,
    ns
)


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_GET_PAL_INFOS = """
SELECT
    h.name,
    h.source,
    COALESCE(a.alias, h.name),
    h.pal_id
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1;
"""


SQL_UPDATE_UNKEPT = '''
UPDATE hash
SET is_kept = 0
WHERE pal_id = ?;
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT
AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT


REPORT_SUBLIST_JSON = REPORT_DIR / 'AUDIT-SUBLIST.json'
REPORT_SUBLIST_JSON.touch()


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'
IGNORED_YAML.touch()


SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


PAL_COLOR_LISTS = dict()
PAL_COLOR_SETS  = dict()
UID_2_PAL_KEPT_INFOS = dict()
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

    logging.info(f"(data) Get '{src}' palettes")

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

logging.info("(data) Get 'kept' palettes")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_PAL_INFOS)

    for name, src, alias, pal_id in cursor.fetchall():
        uid = get_uid(name, src)

        UID_2_PAL_KEPT_INFOS[uid] = (alias, pal_id)


PAL_UIDS = natsorted(
    list(UID_2_PAL_KEPT_INFOS),
    alg     = ns.IGNORECASE,
    reverse = True,
)


# ---------------- #
# -- CANDIDATES -- #
# ---------------- #

logging.info("(audit) Looking for 'candidate' palettes")

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
    logging.info("(audit) 'No candidate'")
    exit(0)

else:
    plurial = '' if nb_candidates == 1 else 's'

    logging.info(
        f"(audit) '{nb_candidates} candidate{plurial}' found"
    )


# ---------------------- #
# -- TRANSFO PALETTES -- #
# ---------------------- #

for ctxt, validator, memodict in [
    ('sublist', isublistof, SUBLIST_PALS),
    ('shifted', isshiftof, SHIFTED_PALS),
    ('reversed and shifted', isreversedshiftof, REVERSED_SHIFTED_PALS),
]:
    logging.info(
        f"(audit) Looking for '{ctxt}' palettes"
    )

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
        nb_found = len(memodict)
        plurial  = '' if nb_found == 1 else 's'

        logging.info(
            f"(audit) '{nb_found} {ctxt}' palette{plurial} found"
        )

    else:
        logging.info(
            f"(audit) 'No {ctxt}' palette"
        )


# ----------------------------- #
# -- REPORT SUBLIST PALETTES -- #
# ----------------------------- #

if SUBLIST_PALS:
    logging.info(f"(report) Update 'sublist palettes' JSON")

    sublist_data = dict()

    for uid_child, (uid_parent, positions) in SUBLIST_PALS.items():
        alias_child  = UID_2_PAL_KEPT_INFOS[uid_child][0]
        alias_parent = UID_2_PAL_KEPT_INFOS[uid_parent][0]

        sublist_data[alias_child] = {
            'palette': alias_parent,
            'extract': human_range(positions)
        }

    REPORT_SUBLIST_JSON.write_text(
        json_dumps(sublist_data)
    )


# ----------------------------- #
# -- UPDATE IGNORED PALETTES -- #
# ----------------------------- #

if SHIFTED_PALS or REVERSED_SHIFTED_PALS:
    new_unkept_ids = []

    logging.info(f"(audit) Update 'unkept palettes' YAML")

    ignored = safe_load(
        IGNORED_YAML.read_text()
    )

    for asciicode, palsunkept in [
        ('<<', SHIFTED_PALS),
        ('<<-->>', REVERSED_SHIFTED_PALS),
    ]:
        for uid_child, (uid_parent, shiftval) in palsunkept.items():
            alias_unkept, pal_unkept_id = UID_2_PAL_KEPT_INFOS[uid_child]

            new_unkept_ids.append(pal_unkept_id)

            alias_parent, pal_parent_id = UID_2_PAL_KEPT_INFOS[uid_parent]

            name, src = extract_name_n_srcname(uid_child)

            src = src.upper()

            if not src in ignored:
                ignored[src] = dict()

            ignored[src][alias_unkept] = {
                'palette' : alias_parent,
                'relation': asciicode,
                'data'    : shiftval,
            }

    IGNORED_YAML.write_text(
        yaml_dump(ignored)
    )

    with sqlite3.connect(SQLITE_DB_FILE) as conn:
        cursor = conn.cursor()

        for pal_id in new_unkept_ids:
            cursor.execute(
                SQL_UPDATE_UNKEPT,
                (pal_id, )
            )
