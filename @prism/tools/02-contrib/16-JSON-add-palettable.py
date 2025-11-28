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


ORIGINAL_NAMES = defaultdict(dict)


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


PATTERN_COMMON_PYDEF = re.compile(
    r'_?([A-Z0-9_]+)\s*=\s*(\[[\s\S]*?\n\])'
)

PATTERN_NAMES_TO_DATA = re.compile(
    r'_NAMES_TO_DATA\s*=\s*\{([^}]+)\}'
)

PATTERN_NAME_PAIR = re.compile(
    r"['\"]([\w0-9_]+)['\"]:\s*(colormaps|colordata)\._?([\w_]+)"
)


# ----------- #
# -- TOOLS -- #
# ----------- #

# -- SPECIAL PALETTABLE SPECS -- #

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

        palettes[name] = pal255_to_pal01(cols)

    return palettes


# -- STD PALETTABLE SPECS -- #

def extract_data(file: Path) -> dict[ str, list[ [float, float, float] ] ]:
    pycode = file.read_text()
    pycode = pycode.replace(')]', ')\n]')
    pycode = pycode.replace(']]', ']\n]')

    palettes = dict()

    for match in PATTERN_COMMON_PYDEF.finditer(pycode):
        name = match.group(1)
        cols = match.group(2)
        cols = eval(cols)

        palettes[name] = pal255_to_pal01(cols)

    return palettes


def extract_original_names(
    folder   : Path,
    pattern  : re.Pattern,
    xtrafiles: list[str]
) -> dict[ str, str ]:
    original_names = dict()

    for fname in xtrafiles + [
        'diverging',
        'qualitative',
        'sequential',
    ]:
        pyfile = folder / f"{fname}.py"

        if not pyfile.is_file():
            continue

        pycode = pyfile.read_text()

        match = PATTERN_NAMES_TO_DATA.search(pycode, re.DOTALL)

        if not match:
            continue

        pycode = match.group(1)

        for pair_match in pattern.finditer(pycode):
            srcname = pair_match.group(1)
            pyname  = pair_match.group(3)

            original_names[pyname] = srcname

    return original_names


def extract_std(
    folder     : Path,
    pyfile_name: str,
    xtrafiles  : list[str] = []
) -> dict[ str, list[ [float, float, float] ] ]:
    oripals = extract_data(folder / f"{pyfile_name}.py")

    orinames = extract_original_names(
        folder    = folder,
        pattern   = PATTERN_NAME_PAIR,
        xtrafiles = xtrafiles
    )

    pals = {
        orinames[n]: p
        for n, p in oripals.items()
    }

    return pals


extract_cartocolors = lambda f: extract_std(
    folder      = f,
    pyfile_name = "colormaps"
)

extract_cmocean = extract_cartocolors

extract_lightbartlein = lambda f: extract_std(
    folder      = f,
    pyfile_name = "colordata"
)

extract_plotly  = extract_lightbartlein

extract_mycarta = lambda f: extract_std(
    folder      = f,
    pyfile_name = "colordata",
    xtrafiles   = ["mycarta"]
)


def extract(folder: Path) -> dict[ str, list[ [float, float, float] ] ]:
    logging.info(f"Analyzing '{folder.name}' folder.")

    extractor = globals()[f"extract_{folder.name}"]

    pals = extractor(folder)

    if not pals:
        logging.info(f"No extraction.")

    return pals


# ------------------------------------ #
# -- BUILD FROM PALETTABLE PALETTES -- #
# ------------------------------------ #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

for folder in sorted(ORIGINAL_SRC_DIR.glob("*")):
    if not folder.name in PALETTABLE_SUB_FOLDERS:
        continue

    ctxt     = PALETTABLE_SUB_FOLDERS[folder.name]
    palettes = extract(folder)

    for pal_name, pal_def in palettes.items():
        std_name = stdname(pal_name)

        ORIGINAL_NAMES[ctxt][std_name] = pal_name
        PAL_CREDITS[std_name]          = ctxt

        ALL_PALETTES, PAL_REPORT = update_palettes(
            context   = ctxt,
            name      = std_name,
            candidate = pal_def,
            palettes  = ALL_PALETTES,
            ignored   = PAL_REPORT,
            logcom    = logging
        )


nb_new_pals = resume_pal_build(
    context     = ctxt,
    nb_new_pals = nb_new_pals,
    palettes    = ALL_PALETTES,
    logcom      = logging,
)


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

for ctxt, orinames in ORIGINAL_NAMES.items():
    ctxt_file_name = ctxt.replace(' ', '-').upper()
    names_file     = REPORT_DIR / f"NAMES-{ctxt_file_name}.json"

    update_jsons(
        names   = orinames,
        jsnames = names_file,
    )

update_jsons(
    nb_new_pals = nb_new_pals,
    credits     = PAL_CREDITS,
    jscredits   = PAL_CREDITS_FILE,
    reports     = PAL_REPORT,
    jsreports   = PAL_REPORT_FILE,
    palettes    = ALL_PALETTES,
    jspalettes  = PAL_JSON_FILE,
    logcom      = logging,
)
