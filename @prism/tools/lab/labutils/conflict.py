#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from pathlib import Path

from json import load as json_load
from yaml import (
    safe_load,
    dump as yaml_dump
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

TAG_ALIAS    = 'alias'
TAG_IGNORE   = 'ignore'
TAG_RGB_COLS = 'rgb-cols'
TAG_REF      = 'ref'
TAG_SIMILAR  = 'similar'
TAG_IS_IGNORED   = 'is-ignored'
TAG_SIZE     = 'size'
TAG_UNIQUE   = 'unique'

TAG_SUFFIXES = '_SUFFIXES_'


THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism" and PROJ_DIR.parent != PROJ_DIR):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = PROJ_DIR / "tools" / "building" / "AUDIT"
REPORT_DIR = AUDIT_DIR.parent / "REPORT"

VISUAL_SIMILAR_YAML = AUDIT_DIR / "VISUAL-SIMILAR.yaml"
VISUAL_EQUAL_YAML   = AUDIT_DIR / "VISUAL-EQUAL.yaml"
IGNORED_YAML        = AUDIT_DIR / "ignored.yaml"
RENAMED_YAML        = AUDIT_DIR / "renamed.yaml"

NAME_CONFLICT_JSON = REPORT_DIR / "AUDIT-NAME-CONFLICT.json"


# ------------------ #
# -- YAML HELPERS -- #
# ------------------ #

def load_yaml_safely(path, default_factory):
    if not path.is_file():
        path.touch()

        return default_factory()

    data = safe_load(path.read_text())

    return data if data is not None else default_factory()


def save_yaml(path, object):
    if object:
        with path.open("w") as f:
            yaml_dump(object, f)

    else:
        path.write_text("")



# -------------------- #
# -- PALS FUNCTIONS -- #
# -------------------- #

def extract_name_n_srcname(name_srcname: str) -> (str, str):
    return tuple(name_srcname.split('::'))


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return '::'.join([name, srcname])


_nb_chges_saved = 0

def update_data(report  : dict) -> None:
    global _nb_chges_saved

    _nb_chges_saved += 1

    ignored        = load_yaml_safely(IGNORED_YAML,dict)
    renamed        = load_yaml_safely(RENAMED_YAML,dict)
    visual_equal   = load_yaml_safely(VISUAL_EQUAL_YAML,dict)
    VISUAL_SIMILAR = load_yaml_safely(VISUAL_SIMILAR_YAML,list)

    if not TAG_SUFFIXES in renamed:
        renamed[TAG_SUFFIXES] = dict()


    for nsn, infos in report.items():
        name, src = extract_name_n_srcname(nsn)

        visual_similar = []

# To ignore.
        if infos[TAG_IS_IGNORED]:
# ignored because of a visual "equality".
            if infos[TAG_REF]:
                visual_equals = visual_equal.get(name, dict())
                visual_equals[src] = infos[TAG_REF]

                visual_equal[name] = visual_equals

# ignored with or without a visual "equality".
            names = ignored.get(src, [])
            names.append(name)
            names = list(set(names))
            names.sort()

            ignored[src] = names

            continue

# renamed.
        if infos[TAG_ALIAS]:
            if not src in renamed[TAG_SUFFIXES]:
                suffix = input(f"Which suffix for '{src}'?\n")

                renamed[TAG_SUFFIXES][src] = suffix

            renames = renamed.get(src, dict())
            renames[name] = infos[TAG_ALIAS]

            renamed[src] = renames

# Similar to another source.
        if infos[TAG_REF]:
            visual_similar.append(
                set([
                    build_name_n_srcname(name, src),
                    build_name_n_srcname(name, infos[TAG_REF])
                ])
            )

# Finalize the full list of similar palettes.
    groupes = []

    visual_similar += [
        set(g) for g in VISUAL_SIMILAR
    ]

    for s in visual_similar:
        # On cherche les groupes existants qui ont une intersection avec le set actuel
        nouveaux_groupes = []
        fusion_actuelle = s

        for g in groupes:
            if not g.isdisjoint(s):
                # Si ça se croise, on l'ajoute à notre fusion
                fusion_actuelle = fusion_actuelle.union(g)
            else:
                # Sinon, on garde le groupe tel quel pour le moment
                nouveaux_groupes.append(g)

        # On ajoute le set fusionné à la liste des groupes
        nouveaux_groupes.append(fusion_actuelle)
        groupes = nouveaux_groupes

    _visual_similar = sorted([
        sorted(list(g)) for g in groupes
    ])


# Update human readable files.
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








if __name__ == "__main__":
    report = {
    'Gray::TABLEAU': {
        'is-ignored': False,
        'is-similar': False,
        'ref': '',
        'alias': 'MidGray',
    },
    'Gray::MATPLOTLIB': {
        'is-ignored': False,
        'is-similar': False,
        'ref': '',
        'alias': '',
    },
    'Gray::CMOCEAN': {
        'is-ignored': True,
        'is-similar': False,
        'ref': 'MATPLOTLIB',
        'alias': '',
    },
    'Rainbow::MATPLOTLIB': {
        'is-ignored': False,
        'is-similar': False,
        'ref': '',
        'alias': '',
    },
    'Rainbow::PLOTLY': {
        'is-ignored': False,
        'is-similar': False,
        'ref': '',
        'alias': '.',
    }}

    update_data(report)
