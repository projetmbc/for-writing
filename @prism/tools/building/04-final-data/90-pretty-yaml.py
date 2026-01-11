#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from string import ascii_uppercase



THIS_DIR = Path(__file__).parent
AUDIT_DIR  = THIS_DIR.parent / TAG_AUDIT

VISUAL_SIMILAR_YAML = AUDIT_DIR / "VISUAL-SIMILAR.yaml"
VISUAL_EQUAL_YAML   = AUDIT_DIR / "VISUAL-EQUAL.yaml"
IGNORED_YAML        = AUDIT_DIR / "IGNORED.yaml"
RENAMED_YAML        = AUDIT_DIR / "RENAMED.yaml"



def get_initial_inlist(
    line: str
) -> str:
    while(line[0] == '-'):
        line = line[1:].strip()

    return line[0]


def get_initial_indict(
    line: str
) -> str:
    return line[0]


def get_comment_initial(
    line: str
) -> str:
    if not line.startswith('#  + '):
        return ''

    return line[5:].strip()

def humanize_yaml(
    path: Path,
) -> None:
# Method to get initial.
    what = path.stem

    if what == VISUAL_SIMILAR_YAML.stem:
        get_initial = get_initial_inlist

    else:
        get_initial = get_initial_indict

# Let's work.
    hard_lines = path.read_text().split('\n')

    _new_code    = []
    last_initial = ''

    for line in hard_lines:
        add_initial = False

        if line.strip():
            if line[0] == '#':
                add_initial = False

                this_initial = get_comment_initial(line)

                if this_initial in ascii_uppercase:
                    last_initial = this_initial

            elif line[0] != ' ':
                this_initial = get_initial(line)

                add_initial = (
                    this_initial != last_initial
                    and
                    this_initial in ascii_uppercase
                )

        if add_initial:
            _new_code.append(f"\n#  + {this_initial}")

            last_initial = this_initial

        _new_code.append(line)

    new_code = '\n'.join(_new_code)
    new_code = new_code.replace('\n'*3, '\n'*2)
    new_code = new_code.strip()

    path.write_text(new_code)


# Update of YAML files - Human friendly version.
for p in [
    IGNORED_YAML,
    VISUAL_EQUAL_YAML,
    VISUAL_SIMILAR_YAML,
    RENAMED_YAML,
]:
    humanize_yaml(p)
