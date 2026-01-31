#!/usr/bin/env python3

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

from json import (
    dumps as json_dumps,
    load  as json_load,
)

from shutil import copytree, rmtree


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

VERSION = (BUILD_TOOLS_DIR / 'VERSION.txt').read_text()

CREDITS = (BUILD_TOOLS_DIR / 'CREDITS.txt').read_text()
CREDITS = CREDITS.strip()
CREDITS = CREDITS.format(VERSION = VERSION)


AUTO_QUAL_CATEGO_SIZE = YAML_CONFIGS['SEMANTIC']['AUTO_QUAL_CATEGO_SIZE']


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"

PRODS_DIR     = PROJ_DIR / "products"
PROD_JSON_DIR = PRODS_DIR / "json"


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

CONTRIBS_ACCEPTED = get_accepted_paths(PROJ_DIR)

IMPL_ACCEPTED = CONTRIBS_ACCEPTED.get(
    CONTRIB_PROD_DIR,
    []
)


# ------------------ #
# -- GET PAL DICT -- #
# ------------------ #

logging.info(f"Get 'JSON palette defs'")

monopaldefs = dict()

for jsonfile in PROD_JSON_DIR.glob('*.json'):
    logging.info(f"Found '{jsonfile.stem}'")

    with jsonfile.open(mode = "r") as f:
        monopaldefs[jsonfile.stem] = json_load(f)


# ----------------------------------- #
# -- MONOLITHIC & MODULAR VERSIONS -- #
# ----------------------------------- #

# -- DEBUG - ON -- #
# if (PRODS_DIR / 'css').is_dir():
#     rmtree(PRODS_DIR / 'css')
#     rmtree(PRODS_DIR / 'latex')
#     rmtree(PRODS_DIR / 'lua')
# -- DEBUG - OFF -- #

for ctxt in sorted(
    IMPL_ACCEPTED,
    key = lambda x: x.lower()
):
    logging.info(f"Implement '{ctxt}'")

# Import extend.py.
    logging.info(f"({ctxt}) Import 'extend.py'")

    extend = import_from_path(
        module_name = "extend",
        file_path   = CONTRIB_PROD_DIR / ctxt / "extend.py"
    )

    paltransfo = extend.paltransfo

# Let's work...
    this_prod_folder = PRODS_DIR / ctxt
    this_prod_folder.mkdir()

    credits = paltransfo.get_credits(CREDITS)

    for palversion, paldefs in monopaldefs.items():
# Monolithic versions.
        logging.info(
            f"({ctxt}) '{palversion}' - Monolithic"
        )

        codefile = this_prod_folder / (
            f"{palversion}.{paltransfo.extension}"
        )

        codefile.touch()

        _code = [credits, '']

        if paltransfo.header:
            _code.append(paltransfo.header)

        for palname, palette in paldefs.items():
            _code.append(
                paltransfo.get_palcode(
                    name    = palname,
                    palette = palette
                )
            )

            _code.append('')

        _code.pop(-1)

        if paltransfo.footer:
            _code.append(paltransfo.footer)

        _code.append('')

        code = '\n'.join(_code)

        codefile.write_text(code)

# Modular versions.
        logging.info(
            f"({ctxt}) '{palversion}' - Modular"
        )

        subdir = this_prod_folder / palversion
        subdir.mkdir()

        for palname, palette in paldefs.items():
            codefile = subdir / f"{palname}.{paltransfo.extension}"
            codefile.touch()

            _code = [credits, '']

            if paltransfo.header:
                _code.append(paltransfo.header)

            _code.append(
                paltransfo.get_palcode(
                    name    = palname,
                    palette = palette
                )
            )

            if paltransfo.footer:
                _code.append(paltransfo.footer)

            _code.append('')

            code = '\n'.join(_code)

            codefile.write_text(code)

# API.
    code = paltransfo.get_apicode()

    if not code:
        logging.info(f"({ctxt}) No 'API'")

    else:
        logging.info(f"({ctxt}) Add 'API'")

        codefile = this_prod_folder / (
            f"palapi.{paltransfo.extension}"
        )

        codefile.touch()

        codefile.write_text(code)

# Showcase.
    logging.info(f"({ctxt}) Add 'showcase'")

    copytree(
        src = CONTRIB_PROD_DIR / ctxt / "fake-prod" / "showcase",
        dst = this_prod_folder / "showcase",
    )


# ---------------------- #
# -- JUST COMMUNICATE -- #
# ---------------------- #

nb_impl = len(IMPL_ACCEPTED)

plurial = "" if nb_impl == 1 else "s"

logging.info(f"Report - '{nb_impl} techno{plurial} added'")
