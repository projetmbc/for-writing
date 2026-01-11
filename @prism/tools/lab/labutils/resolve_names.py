#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from typing import (
    Any,
    Callable,
)

from pathlib import Path

from json import load as json_load
from yaml import (
    safe_load,
    dump as yaml_dump
)

from string import ascii_uppercase


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TAG_ALIAS      = 'alias'
TAG_REF        = 'ref'
TAG_IS_IGNORED = 'is-ignored'

TAG_RGB_COLS = 'rgb-cols'
TAG_SIZE     = 'size'

TAG_SUFFIXES = '_SUFFIXES_'


TAG_NSN_SEP = '::'


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism" and PROJ_DIR.parent != PROJ_DIR):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = PROJ_DIR / "tools" / "building" / "AUDIT"
REPORT_DIR = AUDIT_DIR.parent / "REPORT"

VISUAL_SIMILAR_YAML = AUDIT_DIR / "VISUAL-SIMILAR.yaml"
VISUAL_EQUAL_YAML   = AUDIT_DIR / "VISUAL-EQUAL.yaml"
IGNORED_YAML        = AUDIT_DIR / "IGNORED.yaml"
RENAMED_YAML        = AUDIT_DIR / "RENAMED.yaml"

NAME_CONFLICT_JSON = REPORT_DIR / "AUDIT-NAME-CONFLICT.json"


# ------------------ #
# -- YAML HELPERS -- #
# ------------------ #

def load_yaml_safely(
    path       : Path,
    obj_factory: Callable
) -> Any:
    if not path.is_file():
        path.touch()

        return obj_factory()

    data = safe_load(path.read_text())
    data = data if data is not None else obj_factory()

    return data


def save_yaml(
    path: Path,
    obj : Any
) -> None:
    if obj:
        with path.open("w") as f:
            yaml_dump(obj, f)

    else:
        path.write_text("")


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
            if line[0] != ' ':
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


# --------------------------- #
# -- NAME AND SOURCE - UID -- #
# --------------------------- #

def extract_name_n_srcname(
    name_srcname: str
) -> (str, str):
    return tuple(name_srcname.split(TAG_NSN_SEP))


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return TAG_NSN_SEP.join([name, srcname])


# ----------------------- #
# -- 'CONFLICT' UPDATE -- #
# ----------------------- #

_nb_chges_saved = 0

def update_data(report  : dict) -> None:
# -- DEBUG - ON -- #
    # print(report)
    # exit(1)
# -- DEBUG - OFF -- #

# Vars used.
    global _nb_chges_saved

    _nb_chges_saved += 1

    ignored        = load_yaml_safely(IGNORED_YAML,dict)
    renamed        = load_yaml_safely(RENAMED_YAML,dict)
    visual_equal   = load_yaml_safely(VISUAL_EQUAL_YAML,dict)
    VISUAL_SIMILAR = load_yaml_safely(VISUAL_SIMILAR_YAML,list)

    if not TAG_SUFFIXES in renamed:
        renamed[TAG_SUFFIXES] = dict()

# Let's iterate on the date.
    for nsn, infos in report.items():
        name, src = extract_name_n_srcname(nsn)

        visual_similar = []

# -- TO IGNORE -- #
        if infos[TAG_IS_IGNORED]:
#   + Ignored because of a visual "equality".
            if infos[TAG_REF]:
                visual_equals = visual_equal.get(name, dict())
                visual_equals[src] = infos[TAG_REF]

                visual_equal[name] = visual_equals

#   + Ignored with or without a visual "equality".
            names = ignored.get(src, [])
            names.append(name)
            names = list(set(names))
            names.sort()

            ignored[src] = names

            continue

# -- RENAMED -- #
        if infos[TAG_ALIAS]:
            if not src in renamed[TAG_SUFFIXES]:
                suffix = input(f"Which suffix for '{src}'?\n")

                renamed[TAG_SUFFIXES][src] = suffix

            renames = renamed.get(src, dict())
            renames[name] = infos[TAG_ALIAS]

            renamed[src] = renames

# -- SIMILAR TO ANOTHER SOURCE -- #
        if infos[TAG_REF]:
            visual_similar.append(
                set([
                    build_name_n_srcname(name, src),
                    build_name_n_srcname(name, infos[TAG_REF])
                ])
            )

# We must build the stored list of similar palettes.
    groupes = []

    visual_similar += [
        set(g) for g in VISUAL_SIMILAR
    ]

    for s in visual_similar:
        nouveaux_groupes = []
        fusion_actuelle = s

        for g in groupes:
            if not g.isdisjoint(s):
                fusion_actuelle = fusion_actuelle.union(g)

            else:
                nouveaux_groupes.append(g)

        nouveaux_groupes.append(fusion_actuelle)
        groupes = nouveaux_groupes

    _visual_similar = sorted([
        sorted(list(g)) for g in groupes
    ])


# Update of YAML files - Hard version.
    for p, o in [
        (IGNORED_YAML, ignored),
        (VISUAL_EQUAL_YAML, visual_equal),
        (VISUAL_SIMILAR_YAML, _visual_similar),
    ]:
        save_yaml(p, o)


    suffixes  = renamed[TAG_SUFFIXES]
    _suffixes = {TAG_SUFFIXES: suffixes}

    del renamed[TAG_SUFFIXES]

    suffix_code = yaml_dump(_suffixes).strip()

    comment = f"""
# '.' asks to add the suffix to the existing name.
# '*' is an alias for the suffix.
    """.strip()

    names_code  = yaml_dump(renamed).strip()

    full_code = f"""
{suffix_code}

{comment}

{names_code}
    """.strip() + '\n'

    RENAMED_YAML.write_text(full_code)

    print(f"  > Update #{_nb_chges_saved}.")

# Update of YAML files - Human friendly version.
    for p in [
        IGNORED_YAML,
        VISUAL_EQUAL_YAML,
        VISUAL_SIMILAR_YAML,
        RENAMED_YAML,
    ]:
        humanize_yaml(p)


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    report = {
        'Gray::TABLEAU': {
            'is-ignored': False,
            'ref': '',
            'alias': 'MidGray'
        },
        'Gray::MATPLOTLIB': {
            'is-ignored': False,
            'ref': '',
            'alias': ''
        },
        'Gray::CMOCEAN': {
            'is-ignored': True,
            'ref': 'MATPLOTLIB',
            'alias': ''
        },
        'Rainbow::MATPLOTLIB': {
            'is-ignored': False,
            'ref': '',
            'alias': ''
        },
        'Rainbow::PLOTLY': {
            'is-ignored': False,
            'ref': '',
            'alias': '.'
        }
    }

    update_data(report)
