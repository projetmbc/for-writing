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

THIS_RESRC = TAG_COLORMAPS


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

THIS_RESRC_DIR = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


_RESRC_KINDS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_KINDS_JSON  = REPORT_DIR / f"KIND-{_RESRC_KINDS_JSON}.json"


# ------------------ #
# -- CONSTANTS #2 -- #
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

        src = RESRC_ALIAS.get(src, src)


        if not src in ALL_RESRC_TAGS:
            src = RESRC_ALIAS.get(src.lower(), src)

        if not src in ALL_RESRC_TAGS:
            logging.warning(
                f"Unknown colormaps subproject '{src}'"
            )

        src = RESRC_FILE_NAMES[src]

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


# ------------------ #
# -- MISING KINDS -- #
# ------------------ #

logging.info(f"Extract kinds from '{THIS_RESRC}'")

_PALS_KINDS = defaultdict(set)

for mdpath in sorted(THIS_RESRC_DIR.glob('docs/*.md')):
    fname   = mdpath.name
    palkind = mdpath.stem.lower()

    if palkind == 'scientific':
        continue

    content = mdpath.read_text()

    if palkind == 'other':
        logging.warning(f"Unmanaged '{fname}' (maybe later)")

        continue

    logging.info(f"Parse '{fname}' content")

    if not palkind in KIND_ALIAS:
        log_raise_error(
            context   = f"Missing kind",
            desc      = f"Add '{palkind}' as an alias or a new kind.",
            exception = ValueError,
        )

    palkind = KIND_ALIAS[palkind]

    pals = extract_md_pals(content)

    for uid in pals:
        _PALS_KINDS[uid].add(palkind)


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"Update '{RESRC_KINDS_JSON.relative_to(PROJ_DIR)}'"
)

# We want a deterministic output.
PALS_KINDS = {
    uid: ', '.join(sorted(_PALS_KINDS[uid]))
    for uid in sorted(_PALS_KINDS)
}

# -- DEBUG - ON -- #
# print(PALS_KINDS)
# -- DEBUG - OFF -- #

RESRC_KINDS_JSON.write_text(
    json_dumps(PALS_KINDS)
)
