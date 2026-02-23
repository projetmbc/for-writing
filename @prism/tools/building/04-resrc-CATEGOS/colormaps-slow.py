exit(0)

# TODO: utile?

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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_MD_SECTION_1 = re.compile(
    r'^#\s+(.+)',
    re.MULTILINE
)

PATTERN_MD_SECTION_2 = re.compile(
    r'^##\s+',
    re.MULTILINE
)

TITLES_IGNORED = [
    '---',
    'Table of contents',
]

NAMES_IGNORED = [
    'Name'
]


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[0]
THIS_RESRC = THIS_RESRC.upper()


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

THIS_RESRC_DIR = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


_RESRC_CATEGOS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_CATEGOS_JSON  = REPORT_DIR / f"CATEGO-{_RESRC_CATEGOS_JSON}.json"


# ----------- #
# -- TOOLS -- #
# ----------- #

# WARNING! We must work with full lower case!

def extract_md_pals(content):
    pals = []

    sections = PATTERN_MD_SECTION_2.split(content)

    for section in sections:
        section = section.strip()

        if not section:
            continue

# Which subproject?
        src, *lines = section.split('\n')

        src = src.strip()

        if src in TITLES_IGNORED:
            continue

        src = src.upper()

        if not src in RESRC_ALIAS:
            logging.warning(
                f"Unknown colormaps subproject '{src}'"
            )

# Which palettes?
        for line in lines:
            if not is_data_row(line):
                continue

            name = split_data_row(line)[0]

            name = get_stdname(name)

            if name in NAMES_IGNORED:
                continue

            uid = build_name_n_srcname(name, src)
            uid = uid.lower()

            pals.append(uid)

    return pals


# -------------------- #
# -- ADDING CATEGOS -- #
# -------------------- #

logging.info(f"Categos - Extract from '{THIS_RESRC}'")

_PALS_CATEGOS = defaultdict(set)

for mdpath in sorted(THIS_RESRC_DIR.glob('docs/*.md')):
    fname     = mdpath.name
    palcatego = mdpath.stem.lower()

    if palcatego == 'scientific':
        continue

    content = mdpath.read_text()

    logging.info(f"MD - Parse '{fname}'")

    if not palcatego in CATEGO_ALIAS:
        log_raise_error(
            context   = f"Missing catego",
            desc      = f"Add '{palcatego}' as an alias or a new catego.",
            exception = ValueError,
        )

    palcatego = CATEGO_ALIAS[palcatego]

    pals = extract_md_pals(content)

    for uid in pals:
        _PALS_CATEGOS[uid].add(palcatego)


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"JSON - Update '{RESRC_CATEGOS_JSON.relative_to(PROJ_DIR)}'"
)

# We want a deterministic output.
PALS_CATEGOS = {
    uid: ', '.join(sorted(_PALS_CATEGOS[uid]))
    for uid in sorted(_PALS_CATEGOS)
}

# -- DEBUG - ON -- #
# print(PALS_CATEGOS)
# -- DEBUG - OFF -- #

RESRC_CATEGOS_JSON.write_text(
    json_dumps(PALS_CATEGOS)
)
