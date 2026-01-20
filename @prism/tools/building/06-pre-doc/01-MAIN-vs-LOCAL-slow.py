#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
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

from yaml import (
    safe_load,
    dump as yaml_dump
)


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_GET_ORIGINAL_INFO = '''
SELECT
    COALESCE(a.alias, h.name),
    h.name,
    h.source
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
  AND (h.name = ? OR a.alias = ?);
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #


THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

REPORT_NAME_NEW_JSON     = REPORT_DIR / f"AUDIT-LOCMAIN-NAMES-NEW.json"
REPORT_NAME_REMOVED_JSON = REPORT_DIR / f"AUDIT-LOCMAIN-NAMES-REMOVED.json"


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

WHY_REMOVED_YAML = AUDIT_DIR / f"LOCMAIN-REMOVED-EXPLAINED.yaml"
WHY_REMOVED_YAML.touch()

with WHY_REMOVED_YAML.open("r") as f:
    WHY_REMOVED = safe_load(f)

if WHY_REMOVED is None:
    WHY_REMOVED = dict()



# ----------- #
# -- TOOLS -- #
# ----------- #

def lower_names_kept(
    main_set: set[str],
    alt_set : set[str]
) -> list[str]:
    lower_2_std = {
        x.lower(): x
        for x in main_set
    }

    _main_set = set(x.lower() for x in main_set)
    _alt_set  = set(x.lower() for x in alt_set)

    return sorted(
        lower_2_std[x]
        for x in _main_set - _alt_set
    )


def compare_rgb_palettes(
    pal_1    : PaletteCols,
    pal_2    : PaletteCols,
    tolerance: float      = 0.01,
    size     : None | int = None,
):
# Manadatory size.
    if not size is None:
        ...


    exit(1)


    n = len(small_pal)
    M = len(large_pal)

    # Calcul des indices cibles dans la grande palette
    # On échantillonne de façon régulière du premier au dernier index
    indices = np.linspace(0, M - 1, n).round().astype(int)

    print(f"Comparaison de la structure ({n} vs {M} couleurs)")
    print("-" * 50)

    for i, idx in enumerate(indices):
        rgb_small = np.array(small_pal[i])
        rgb_sampled = np.array(large_pal[idx])

        # Calcul de la distance Euclidienne entre les deux vecteurs RGB
        distance = np.linalg.norm(rgb_small - rgb_sampled)

        status = "✅ MATCH" if distance < tolerance else f"❌ DIFF (dist: {distance:.3f})"

        print(f"Small[{i}] vs Large[{idx}]: {status}")
        print(f"   S: {rgb_small} | L: {rgb_sampled}")


# ------------------- #
# -- LOCAL VERSION -- #
# ------------------- #

logging.info("MAIN vs LOCAL - Get 'last local' version")

JSON_PROD_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with JSON_PROD_FILE.open(mode = "r") as f:
    LOCAL_PALS = json_load(f)


# ------------------------- #
# -- MAIN ONLINE VERSION -- #
# ------------------------- #

logging.info("MAIN vs LOCAL - Get 'main online' version")

url = (
    "https://raw.githubusercontent.com/"
    "projetmbc/for-writing/main/"
    "%40prism/products/json/palettes.json"
)

response = requests.get(url)
response.raise_for_status()

MAIN_PALS = response.json()


# ----------------------- #
# -- NEW/REMOVED NAMES -- #
# ----------------------- #

NEW_NAMES     = lower_names_kept(LOCAL_PALS, MAIN_PALS)
REMOVED_NAMES = lower_names_kept(MAIN_PALS, LOCAL_PALS)

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for names, what, xtra in [
        (NEW_NAMES    , 'new'    , '(cf. doc)'   ),
        (REMOVED_NAMES, 'removed', '(explanations needed)'),
    ]:
        if not names:
            logging.info(f"Names: 'no {what}'")

        else:
            nb   = len(names)
            xtra = f' {xtra}'

            logging.info(f"Names: '{nb} {what}'{xtra}")

# -- DEBUG - ON -- #
print(NEW_NAMES)
print(REMOVED_NAMES)
exit()
# -- DEBUG - OFF -- #


# ------------------------- #
# -- NEW NAMES JSONIFIED -- #
# ------------------------- #

logging.info(
    f"Update '{REPORT_NAME_NEW_JSON.relative_to(PROJ_DIR)}'"
)

report = dict()

for n in NEW_NAMES:
    cursor.execute(
        SQL_GET_ORIGINAL_INFO,
        (n, n)
    )

    results = cursor.fetchall()

    if len(results) != 1:
        print(results)
        BUG_BUG

    alias, *ons = results[0]

    report[alias] = list(ons)

REPORT_NAME_NEW_JSON.write_text(json_dumps(report))


# ----------------------------- #
# -- REMOVED NAMES YAMLIFIED -- #
# ----------------------------- #

logging.info(
    f"Update '{WHY_REMOVED_YAML.relative_to(PROJ_DIR)}'"
)

for n in REMOVED_NAMES:
    if n in WHY_REMOVED:
        continue

    WHY_REMOVED[n] = None

yaml_code = yaml_dump(WHY_REMOVED)
yaml_code = f'''
# Complete with one of the following regarding new palettes, where
# ''<new_alias>'' is the @prism palette name in the current version.
#
#    1) ''<new_alias>: ignored''
#
#    (the palette exists but is intentionally excluded from the
#    processing pipeline)
#
#    2) ''<new_alias>: renamed''
#
#    (the palette identifier has changed, requiring a mapping from
#    the old name to the new one)
#
#    3) ''<new_alias>: superseded''
#
#    (the palette no longer exists but has a direct equivalent).

{yaml_code}
'''.lstrip()

WHY_REMOVED_YAML.write_text(yaml_code)


# ------------------------- #
# -- MISSING KINDS FOUND -- #
# ------------------------- #

if None in WHY_REMOVED.values():
    nb = len([
        x
        for x in WHY_REMOVED.values()
        if x is None
    ])

    plurial = '' if nb == 1 else 's'

    log_raise_error(
        context   = f"{nb} missing explanation{plurial} about removed names need NOAI resolution",
        desc      = "Removed names must be documented with a specific reason.",
        exception = ValueError,
        xtra      = f"Open '{WHY_REMOVED_YAML}'"
    )
