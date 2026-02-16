#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
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

from itertools import product


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PATTERN_ABBREV = re.compile(r'\\\w+')


# ----------- #
# -- TOOLS -- #
# ----------- #

def expand_data(data: dict) -> dict:
    expdata = defaultdict(list)

    for name, vals in data.items():
# XXXX
        if not isinstance(vals, list):
            log_raise_error(
                context   = "'ABOUT.YAML' clean config file.",
                desc      = (
                    f"Value of '{name}' must be a list. "
                    f"Value is:\n{vals}"
                ),
                exception = ValueError,
            )

# XXXX
        for v in vals:
# XXXX
            if v[0] == "\\":
                v = v[1:]

                if not v in expdata:
                    log_raise_error(
                        context   = "'ABOUT.YAML' clean data.",
                        desc      = f"Abbrev '{name}' doesn't exist.",
                        exception = ValueError,
                    )

                expdata[name] += expdata[v]

# XXXX
            else:
                expdata[name].append(v)

# Nothing left to do.
    return expdata


def expand_gobble(
    expdata: dict,
    gobble : list[str]
) -> list[str]:
    expgobble = []

# XXXX
    for i, g in enumerate(gobble):
        abbrevs = PATTERN_ABBREV.findall(g)

# XXXX
        if not abbrevs:
            expgobble.append(g)

            continue

# XXXX
        to_replace = dict()

        for a in abbrevs:
            to_replace[a] = expdata[a[1:]]

            if not to_replace[a]:
                log_raise_error(
                    context   = "'ABOUT.YAML' gobble data.",
                    desc      = f"Abbrev '{a[1:]}' doesn't exist.",
                    exception = ValueError,
                )

# XXXX
        cles = to_replace.keys()
        listes_valeurs = to_replace.values()
        combinaisons = list(product(*listes_valeurs))
        replacements = [dict(zip(cles, combo)) for combo in combinaisons]

        for r in replacements:
            _g = g

            for old, new in r.items():
                _g = _g.replace(old, new)

            expgobble.append(_g)

# Nothing left to do.
    return expgobble


# -------------------------------- #
# -- CLEAN CONTRIB PROD FOLDERS -- #
# -------------------------------- #

contribs_accepted = get_accepted_paths(PROJ_DIR)

for techno in sorted(contribs_accepted[CONTRIB_PROD_DIR]):
    techno_dir = CONTRIB_PROD_DIR / techno
    about_file = techno_dir / 'ABOUT.yaml'

    if not about_file.is_file():
        logging.warning(f"'{techno}' contrib - No clean config")

        continue

    logging.info(f"Clean '{techno}' contrib")

    with about_file.open(mode = 'r') as stream:
        about_cfg = yaml.safe_load(stream)

    clean_cfg = about_cfg[TAG_CLEAN]

    data   = clean_cfg.get(TAG_DATA, dict())
    gobble = clean_cfg.get(TAG_GOBBLE, [])

    if not gobble:
        logging.warning(f"Missing '{techno}' contrib gobble patterns")

        continue

    expdata   = expand_data(data)
    expgobble = expand_gobble(expdata, gobble)

    for g in expgobble:
        for f in techno_dir.glob(g):
            f.unlink()

            logging.info(f"Remove '{f.relative_to(PROJ_DIR)}'")
