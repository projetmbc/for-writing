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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

PROJS_IGNORED = [
    TAG_MATPLOTLIB,
    TAG_ASYMPTOTE,
    TAG_SCICOLMAPS,
    TAG_COLORBREWER,
    TAG_PALETTABLE,
]

SQL_GET_NAMES_TO_TEST = '''
SELECT DISTINCT a.alias
FROM alias a
JOIN hash h ON a.pal_id = h.pal_id
WHERE h.is_kept = 1
  AND h.source NOT IN ({placeholders})
  AND h.equal_to NOT IN (
          SELECT pal_id
          FROM hash
          WHERE source IN ({placeholders})
  );
'''.format(
    placeholders = ',' .join(
        repr(p) for p in PROJS_IGNORED
    )
)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TOLERANCE = 10**(-2)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"
RESRC_DIR = PROJ_DIR / "RESOURCES" / TAG_APRISM_LAST_MAIN


JSON_PALS_HF_DIR = PRODS_DIR / 'json' / 'palettes-hf'


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

REPORT_SAME_NAMED_PALS_JSON = REPORT_DIR / "AUDIT-SAME-NAMED-PALETTES.json"

REPORT_SAME_NAMED_PALS_JSON.touch()


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_palette_compatibility(palette_a, palette_b):
    p1 = np.array(palette_a)
    p1 = np.round(p1, 6)

    p2 = np.array(palette_b)

    if len(p1) != len(p2):
        small_p = p1 if len(p1) < len(p2) else p2
        large_p = p2 if len(p1) < len(p2) else p1

        old_indices = np.linspace(0, 1, len(large_p))
        new_indices = np.linspace(0, 1, len(small_p))

        interp_func = interp1d(old_indices, large_p, axis=0, kind='linear')

        p_ref  = small_p
        p_test = interp_func(new_indices)

    else:
        p_ref, p_test = p1, p2

    distances = np.linalg.norm(p_test - p_ref, axis=1)
    max_err = np.max(distances)
    mean_err = np.mean(distances)

    score = max(0, 100 * (1 - (mean_err / 0.5)))

    match = bool(max_err <= TOLERANCE)

    return match, round(score, 2)


# ------------------------ #
# -- LAST MAIN PALETTES -- #
# ------------------------ #

logging.info("Get 'Last Main Palettes'")

with (RESRC_DIR / 'palettes.json').open(mode = "r") as f:
    LAST_LAST_MAIN_PALS =json_load(f)


# -------------------- #
# -- GET SAME NAMES -- #
# -------------------- #

same_names = set()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    cursor.execute(SQL_GET_NAMES_TO_TEST)

    for alias in cursor.fetchall():
        if alias in LAST_LAST_MAIN_PALS:
            same_names.add(alias)

if not same_names:
    logging.info("Nothing to do")

    exit(0)


# ------------------------- #
# -- PALETTE COMPARISONS -- #
# ------------------------- #

logging.info("Analyze - 'Vals of same named palettes'")

same_named_pals_results = dict()

for jsonfile in JSON_PALS_HF_DIR.glob('*.json'):
    if not jsonfile.stem in LAST_MAIN_PALS:
        continue

    with jsonfile.open() as f:
        pal_1 = json_load(f)

    pal_2 = LAST_MAIN_PALS[name]

    same_named_pals_results[name] = get_palette_compatibility(
        pal_1,
        pal_2
    )


# ------------------------- #
# -- PALETTE COMPARISONS -- #
# ------------------------- #

logging.info(
    f"Update '{REPORT_SAME_NAMED_PALS_JSON.relative_to(PROJ_DIR)}'"
)

REPORT_SAME_NAMED_PALS_JSON.write_text(
    json_dumps(same_named_pals_results)
)
