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



def parse_markdown_palettes(text):
    type_match = re.search(r'^#\s+(.+)', text, re.MULTILINE)

    if type_match:
        palkind = type_match.group(1).replace(' Schemes', '').strip()

    else:
        palkind = ''

    projects = {}


    sections = re.split(r'\n##\s+', text)

    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        project_name = lines[0].strip()

        if "Table of contents" in project_name or not project_name:
            continue

        palettes = []

        for line in lines:
            if line.startswith('|') and '---' not in line and 'Name' not in line:
                parts = line.split('|')

                if len(parts) > 1:
                    palette_name = parts[1].strip()

                    if palette_name:
                        palettes.append(palette_name)

        if palettes:
            projects[project_name] = palettes

    return palkind, projects

# --- Exécution et affichage ---

_PALS_KINDS = defaultdict(set)

for mdpath in sorted(THIS_RESRC_DIR.glob('docs/*.md')):
    palkind, data = parse_markdown_palettes(mdpath.read_text())

    palkind = palkind.lower()

    if not palkind in KIND_ALIAS:
        print(f"{palkind=}")

        TODO

    palkind = KIND_ALIAS[palkind]

    for src, names in data.items():
        for n in names:
            nsn = f"{n}::{src}"

            _PALS_KINDS[nsn].add(palkind)


# We want a deterministic output.
PALS_KINDS = {
    nsn: ', '.join(sorted(_PALS_KINDS[nsn]))
    for nsn in sorted(_PALS_KINDS)
}


RESRC_KINDS_JSON.write_text(
    json_dumps(PALS_KINDS)
)
