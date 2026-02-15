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

from json import load  as json_load

from shutil import copytree, rmtree


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

VERSION = (BUILD_TOOLS_DIR / 'VERSION.txt').read_text()

CREDITS = (BUILD_TOOLS_DIR / 'CREDITS.txt').read_text()
CREDITS = CREDITS.strip()
CREDITS = CREDITS.format(VERSION = VERSION)


MAX_SEM_SIZE = YAML_CONFIGS['SEMANTIC']['MAX_SEM_SIZE']


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"

PRODS_DIR     = PROJ_DIR / "products"
PROD_JSON_DIR = PRODS_DIR / "json"

JSON_PAL_FORMAT_DIRS = [
    PROD_JSON_DIR / f'palettes-{f}'
    for f in [
         'hf',
        f's{MAX_SEM_SIZE}'
    ]
]


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

CONTRIBS_ACCEPTED = get_accepted_paths(PROJ_DIR)

IMPL_ACCEPTED = CONTRIBS_ACCEPTED.get(
    CONTRIB_PROD_DIR,
    []
)


# ---------------------- #
# -- MODULAR VERSIONS -- #
# ---------------------- #

# -- DEBUG - ON -- #
if (PRODS_DIR / 'css').is_dir():
    rmtree(PRODS_DIR / 'css')
    # rmtree(PRODS_DIR / 'latex')
    # rmtree(PRODS_DIR / 'lua')
# -- DEBUG - OFF -- #

for ctxt in sorted(
    IMPL_ACCEPTED,
    key = lambda x: x.lower()
):
    logging.info(f"Implement '{ctxt}'")

    contribfolder = CONTRIB_PROD_DIR / ctxt

# Import extend.py.
    logging.info(f"({ctxt}) Import 'extend.py'")

    extend = import_from_path(
        module_name = "extend",
        file_path   = contribfolder / "extend.py"
    )

    paltransfo = extend.paltransfo

    credits = paltransfo.get_credits(CREDITS)

# Palette files.
    prodfolder = PRODS_DIR / ctxt

    for jsonpaldir in JSON_PAL_FORMAT_DIRS:
        logging.info(f"({ctxt}) Build '{jsonpaldir.name}' folder")

        paldir = prodfolder / jsonpaldir.name
        paldir.mkdir(parents = True)

        for jsonfile in jsonpaldir.glob('*.json'):
            with jsonfile.open(mode = "r") as f:
                paldef = json_load(f)

            palname = jsonfile.stem

            palfile = paldir / f"{palname}.{paltransfo.extension}"

            palfile.touch()

            _palcode = [credits, '']

            if paltransfo.header:
                _palcode.append(paltransfo.header)

            _palcode.append(
                paltransfo.get_palcode(
                    name    = palname,
                    palette = paldef
                )
            )

            if paltransfo.footer:
                _palcode.append(paltransfo.footer)

            _palcode.append('')

            palcode = '\n'.join(_palcode)

            palfile.write_text(palcode)

# API.
    apicode = paltransfo.get_apicode()

    if not apicode:
        logging.info(f"({ctxt}) No 'API'")

    else:
        logging.info(f"({ctxt}) Add 'API'")

        apifile = prodfolder / (
            f"palapi.{paltransfo.extension}"
        )

        apifile.touch()
        apifile.write_text(apicode)

# Showcase.
    logging.info(f"({ctxt}) Add 'showcase'")

    copytree(
        src = contribfolder / "fake-prod" / "showcase",
        dst = prodfolder / "showcase",
    )


# ---------------------- #
# -- JUST COMMUNICATE -- #
# ---------------------- #

nb_impl = len(IMPL_ACCEPTED)

plurial = "" if nb_impl == 1 else "s"

logging.info(f"Report - '{nb_impl} techno{plurial} added'")
