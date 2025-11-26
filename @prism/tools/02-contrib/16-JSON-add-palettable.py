#!/usr/bin/env python3

from rich import print


from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

# from collections import defaultdict

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_PALETTABLE

THIS_DIR         = Path(__file__).parent
PROJ_DIR         = THIS_DIR.parent.parent
PRODS_DIR        = PROJ_DIR / "products"
ORIGINAL_SRC_DIR = PROJ_DIR / "resources" / "Palettable" / "palettable-master" / "palettable"
REPORT_DIR       = THIS_DIR.parent / "report"


CTXT_FILE_NAME = CTXT.replace(' ', '-').upper()
NAMES_FILE     = REPORT_DIR / f"NAMES-{CTXT_FILE_NAME}.json"
ORIGINAL_NAMES = dict()


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


STD_NAMES_IGNORED = list(ALL_PALETTES) + list(PAL_REPORT)


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_cubehelix(folder: Path) -> dict[ str, list[ [float, float, float] ] ]:
    src_code = folder / f"{folder.name}.py"
    src_code = src_code.read_text()

    for d in [
        'palette_rgb',
        '=',
    ]:
        _ , _ , src_code = src_code.partition(d)

    src_pals, _ , _ = src_code.partition('class Cubehelix')

    src_pals = eval(src_pals.strip())

    palettes = {}

    for name, cols in src_pals.items():
        if not name.endswith('_16'):
            print(name)
            TODO

        name = name[:-3]

        palettes[name] = pal255_to_pal01(cols)

    return palettes


def extract_tableau(folder: Path) -> dict[ str, list[ [float, float, float] ] ]:
    src_code = folder / f"{folder.name}.py"
    src_code = src_code.read_text()

    _ , _ , src_code = src_code.partition('palette_names =')

    src_names, _ , src_code = src_code.partition('colors_rgb =')

    src_names, _ , _ = src_names.partition('lookup')

    src_pals, _ , _ = src_code.partition('class TableauMap')

    src_names = eval(src_names.strip())
    src_pals  = eval(src_pals.strip())

    last_sizes = defaultdict(int)
    palettes   = {}

    for name, cols in zip(
        src_names,
        src_pals
    ):
        name, _ , pal_size = name.partition('_')

        pal_size = int(pal_size)

        if pal_size > last_sizes[name]:
            last_sizes[name] = pal_size
            palettes[name]   = pal255_to_pal01(cols)

    return palettes


def extract_wesanderson(folder: Path) -> dict[ str, list[ [float, float, float] ] ]:
    src_code = folder / f"{folder.name}.py"
    src_code = src_code.read_text()

    _ , _ , src_code = src_code.partition('_palettes =')

    src_code, _ , _ = src_code.partition('_map_names')

    src_code = src_code.strip()
    src_pals = []

    for line in src_code.split('\n'):
        short_line = line.strip()

        keep = True

        for k in ["type", "url"]:
            if (
                short_line.startswith(f"'{k}':")
                or
                short_line.endswith(f"')")
            ):
                keep = False
                break

        if keep:
            src_pals.append(line)

    src_pals = eval('\n'.join(src_pals))

    palettes = {}

    for name, cols in src_pals.items():
        cols = cols['colors']
        size = str(len(cols))

        name = name[:-len(size)]

        palettes[name] = pal255_to_pal01(cols)

    return palettes


def extract_std(folder: Path) -> dict[ str, list[ [float, float, float] ] ]:
    ...



def extract(folder: Path) -> dict[ str, list[ [float, float, float] ] ]:
    logging.info(f"Analyzing '{folder.name}' folder.")

    files = [
        f
        for f in folder.glob('*')
        if f.name[0] != '.'
    ]

    if len(files) == 1:
        extractor = globals()[f"extract_{folder.name}"]

    else:
        extractor = extract_std

    return extractor(folder)


# ------------------------------------ #
# -- BUILD FROM PALETTABLE PALETTES -- #
# ------------------------------------ #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

for folder in ORIGINAL_SRC_DIR.glob("*"):
    if not folder.name in PALETTABLE_SUB_FOLDERS:
        continue

    ctxt     = PALETTABLE_SUB_FOLDERS[folder.name]
    palettes = extract(folder)

    for pal_name, pal_def in palettes.items():
        std_name = stdname(pal_name)

        ORIGINAL_NAMES[std_name] = pal_name
        PAL_CREDITS[std_name]    = ctxt

        if std_name in STD_NAMES_IGNORED:
            continue

        ALL_PALETTES, PAL_REPORT = update_palettes(
            context   = ctxt,
            name      = std_name,
            candidate = pal_def,
            palettes  = ALL_PALETTES,
            ignored   = PAL_REPORT,
            logcom    = logging
        )


nb_new_pals = len(ALL_PALETTES) - nb_new_pals

if nb_new_pals == 0:
    logging.info("Nothing new found.")

else:
    plurial = "" if nb_new_pals == 1 else "s"

    logging.info(f"{nb_new_pals} palette{plurial} added.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

NAMES_FILE.write_text(
    json_dumps(ORIGINAL_NAMES)
)

PAL_CREDITS_FILE.write_text(
    json_dumps(PAL_CREDITS)
)

if nb_new_pals != 0:
    PAL_REPORT_FILE.write_text(
        json_dumps(PAL_REPORT)
    )

    logging.info("Update palette JSON file.")

    PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
