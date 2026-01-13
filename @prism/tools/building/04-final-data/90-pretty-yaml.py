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


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR  = Path(__file__).parent
AUDIT_DIR = THIS_DIR.parent / TAG_AUDIT

ALL_YAMLS = [
    AUDIT_DIR / "HUMAN-KIND.yaml",
    AUDIT_DIR / "IGNORED.yaml",
    AUDIT_DIR / "RENAMED.yaml",
    VISUAL_SIMILAR_YAML:= AUDIT_DIR / "VISUAL-SIMILAR.yaml",
    AUDIT_DIR / "VISUAL-EQUAL.yaml",
]


# ----------- #
# -- TOOLS -- #
# ----------- #

class IndentDumper(yaml.SafeDumper):
    def increase_indent(
        self,
        flow       = False,
        indentless = False
    ):
        return super(IndentDumper, self).increase_indent(flow, False)


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


def get_initialized_code(code, get_initial):
    _new_code    = []
    last_initial = ''

    for line in code.split('\n'):
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

    return new_code


def humanize_yaml(
    path: Path,
) -> None:
# Method to get initial.
    what = path.stem

    if what == VISUAL_SIMILAR_YAML.stem:
        get_initial = get_initial_inlist

    else:
        get_initial = get_initial_indict

# Data.
    _new_code = []

    with path.open(mode = "r") as f:
        data = safe_load(f)

    if TAG_SUFFIXES in data:
        header = yaml.dump(
            {TAG_SUFFIXES: data[TAG_SUFFIXES]},
            sort_keys = False,
        )

        header = header.strip()

        del data[TAG_SUFFIXES]

    else:
        header = ''

    mini_code = get_initialized_code(
        yaml.dump(
            data,
            Dumper    = IndentDumper,
            indent    = 2,
            sort_keys = True
        ),
        get_initial
    )

    if header:
        _new_code += [
            header,
            '',
            f"""
# '.' asks to add the suffix to the existing name.
# '*' is an alias for the suffix.
            """.strip(),
            ''
        ]

    _new_code.append(mini_code)

    new_code = '\n'.join(_new_code)

# Update file.
    path.write_text(new_code)


# ----------- #
# -- TOOLS -- #
# ----------- #

logging.info(f"Human friendly YAML files.")

for p in ALL_YAMLS:
    logging.info(f"Pretty '{p.relative_to(PROJ_DIR)}'.")

    humanize_yaml(p)
