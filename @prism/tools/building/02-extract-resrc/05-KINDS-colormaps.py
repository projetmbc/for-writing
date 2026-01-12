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

THIS_RESRC = TAG_COLORMAPS


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


THIS_RESRC_DIR = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


_RESRC_KINDS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_KINDS_JSON  = REPORT_DIR / f"KIND-{_RESRC_KINDS_JSON}.json"



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
    'Scientific',
    'Table of contents',
]

NAMES_IGNORED = [
    'Name'
]



def extract_md_pals(content):
    projects = {}

    sections = PATTERN_MD_SECTION_2.split(content)

    for section in sections:
        section = section.strip()

        if not section:
            continue

# Which subproject?
        projname, *lines = section.split('\n')

        projname = projname.strip()

        if projname in TITLES_IGNORED:
            continue

        projname = RESRC_ALIAS.get(projname, projname)

        if not projname in ALL_RESRC_TAGS:
            projname = RESRC_ALIAS.get(projname.lower(), projname)

        if not projname in ALL_RESRC_TAGS:
            logging.warning(
                f"Unknown colormaps subproject '{title}'"
            )

# Which palettes?
        palettes = []

        for line in lines:
            if not is_data_row(line):
                continue

            palname = split_data_row(line)[0]
            palname = get_stdname(palname)

            if palname in NAMES_IGNORED:
                continue

            palettes.append(palname)

        if palettes:
            projects[projname] = palettes

    return projects


# --- Exécution et affichage ---

_PALS_KINDS = defaultdict(set)

for mdpath in sorted(THIS_RESRC_DIR.glob('docs/*.md')):
    what = mdpath.stem.lower()

    if what == 'scientific':
        continue

    if what == 'other':
        ...#TODO

    else:
        palkind = what.lower()
        pals    = extract_md_pals(mdpath.read_text())

    if not palkind in KIND_ALIAS:
        print(f"{palkind=}")

        TODO

    palkind = KIND_ALIAS[palkind]

    for src, names in pals.items():
        src = RESRC_FILE_NAMES[src]

        for n in names:
            n = get_stdname(n)
            n = n.lower()

            nsn = f"{n.lower()}::{src}"

            _PALS_KINDS[nsn].add(palkind)


# We want a deterministic output.
PALS_KINDS = {
    nsn: ', '.join(sorted(_PALS_KINDS[nsn]))
    for nsn in sorted(_PALS_KINDS)
}


RESRC_KINDS_JSON.write_text(
    json_dumps(PALS_KINDS)
)
