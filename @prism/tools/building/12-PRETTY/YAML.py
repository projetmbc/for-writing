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

from string import ascii_uppercase


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR  = Path(__file__).parent
AUDIT_DIR = THIS_DIR.parent / TAG_AUDIT

VISUAL_SIMILAR_YAML = AUDIT_DIR / "VISUAL-SIMILAR.yaml"


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
    if not line.startswith('# -- '):
        return ''

    return line[6]


def get_initialized_code(code, get_initial):
    _new_code      = []
    last_initial   = ''
    add_empty_line = False

    for line in code.split('\n'):
        not_empty_line = bool(line.strip())
        add_initial    = False

        if not_empty_line:
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
            _new_code.append(f"\n# -- {this_initial} -- #")

            last_initial   = this_initial
            add_empty_line = False

        if (
            not_empty_line
            and
            add_empty_line
            and
            line[0] != ' '
        ):
            _new_code.append('')

        if not_empty_line and line[0] != ' ':
            add_empty_line = True

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

    if path.stem == 'HUMAN-CATEGO':
        for src, palcatego in data.items():
            for name, catego in palcatego.items():
                _catego = sorted([
                    c.strip()
                    for c in catego.split(',')
                ])

                catego = ', '.join(_catego)

                palcatego[name] = catego

    if TAG_SUFFIXES in data:
        header = yaml.dump(
            {TAG_SUFFIXES: data[TAG_SUFFIXES]},
            sort_keys = False,
        )

        header = header.strip()
        header = f"""{header}

# '.' asks to add the suffix to the existing name.
# '*' is an alias for the suffix.
            """.strip()

        del data[TAG_SUFFIXES]

    elif path.stem == 'LOCMAIN-REMOVED':
        _header = []

        content = path.read_text().strip()

        for line in content.splitlines():
            if line and line[0] == '#':
                _header.append(line)

            else:
                break

        header = '\n'.join(_header)

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
        _new_code += [header, '']

    _new_code.append(mini_code)
    _new_code.append('')

    new_code = '\n'.join(_new_code)

# Update file.
    path.write_text(new_code)


# ----------- #
# -- TOOLS -- #
# ----------- #

logging.info(f"Human friendly YAML files")

for p in sorted(AUDIT_DIR.glob('*.yaml')):
    # if p.stem.startswith('LOCMAIN-'):
    #     continue

    logging.info(f"Pretty '{p.relative_to(PROJ_DIR)}'")

    humanize_yaml(p)
