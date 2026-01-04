#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_COMMON_PYDEF = re.compile(
    r'_?([A-Z0-9_]+)\s*=\s*(\[[\s\S]*?\n\])'
)

PATTERN_KIND = re.compile(
    r"_PALETTE_TYPE\s*=\s*['\"]([^'\"]+)['\"]"
)

PATTERN_NAMES_TO_DATA = re.compile(
    r'_NAMES_TO_DATA\s*=\s*\{([^}]+)\}'
)

PATTERN_NAME_PAIR = re.compile(
    r"['\"]([\w0-9_]+)['\"]:\s*(colormaps|colordata)\._?([\w_]+)"
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = TAG_PALETTABLE

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_XTRA_RESRC / stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


# ----------- #
# -- TOOLS -- #
# ----------- #

# -- SPECIAL PALETTABLE SPECS -- #

def extract_cubehelix(folder: Path) -> dict[str, PaletteCols]:
    src_code = folder / f"{folder.name}.py"
    src_code = src_code.read_text()

    for d in [
        'palette_rgb',
        '=',
    ]:
        _ , _ , src_code = src_code.partition(d)

    src_pals, _ , _ = src_code.partition('class Cubehelix')

    src_pals = eval(src_pals.strip())

    pals = {}

    for pal_name, cols in src_pals.items():
        if not pal_name.endswith('_16'):
            print(name)
            BUG_TODO

        pal_name = pal_name[:-3]
        std_name = stdname(pal_name)

        pals[std_name] = resrc_std_palette(
            pal_name,
            TAG_SEQ,
            pal255_to_pal01(cols),
        )

    return pals


def extract_tableau(folder: Path) -> dict[str, PaletteCols]:
    src_code = folder / f"{folder.name}.py"
    src_code = src_code.read_text()

    _ , _ , src_code = src_code.partition('palette_names =')

    src_names, _ , src_code = src_code.partition('colors_rgb =')

    src_names, _ , _ = src_names.partition('lookup')

    src_pals, _ , _ = src_code.partition('class TableauMap')

    src_names = eval(src_names.strip())
    src_pals  = eval(src_pals.strip())

    last_sizes = defaultdict(int)
    pals   = {}

    for name, cols in zip(
        src_names,
        src_pals
    ):
        pal_name, _ , pal_size = name.partition('_')

        std_name = stdname(pal_name)

        pal_size = int(pal_size)

        if pal_size > last_sizes[std_name]:
            last_sizes[std_name] = pal_size

            pals[std_name] = resrc_std_palette(
                pal_name,
                TAG_QUAL,
                pal255_to_pal01(cols),
            )

    return pals


def extract_wesanderson(folder: Path) -> dict[str, PaletteCols]:
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

    pals = {}

    for pal_name, cols in src_pals.items():
        std_name = stdname(pal_name)

        cols = cols['colors']

        pals[std_name] = resrc_std_palette(
            pal_name,
            TAG_QUAL,
            pal255_to_pal01(cols),
        )



    return pals


# -- STD PALETTABLE SPECS -- #

def extract_data(file: Path) -> dict[str, PaletteCols]:
    pycode = file.read_text()
    pycode = pycode.replace(')]', ')\n]')
    pycode = pycode.replace(']]', ']\n]')

    pals = dict()

    for match in PATTERN_COMMON_PYDEF.finditer(pycode):
        name = match.group(1)
        cols = match.group(2)
        cols = eval(cols)

        pals[name] = pal255_to_pal01(cols)

    return pals


def extract_kind_and_names(
    folder   : Path,
    pattern  : re.Pattern,
    xtrafiles: list[str]
) -> dict[str, str]:
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

        match = PATTERN_KIND.search(pycode)

        kind = match.group(1) if match else ""

        match = PATTERN_NAMES_TO_DATA.search(pycode, re.DOTALL)

        if not match:
            continue

        pycode = match.group(1)

        for pair_match in pattern.finditer(pycode):
            srcname = pair_match.group(1)
            pyname  = pair_match.group(3)

            original_names[pyname] = (kind, srcname)

    return original_names


def extract_std(
    folder     : Path,
    pyfile_name: str,
    xtrafiles  : list[str] = []
) -> dict[str, PaletteCols]:
    oripals = extract_data(folder / f"{pyfile_name}.py")

    kind_and_names = extract_kind_and_names(
        folder    = folder,
        pattern   = PATTERN_NAME_PAIR,
        xtrafiles = xtrafiles
    )

    pals = {
        stdname(kind_and_names[n][1]): resrc_std_palette(
            kind_and_names[n][1],
            kind_and_names[n][0],
            p,
        )
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


def extract(folder: Path) -> dict[str, PaletteCols]:
    extractor = globals()[f"extract_{folder.name}"]

    pals = extractor(folder)

    if not pals:
        logging.info(f"No extraction.")

    return pals


# --------------------- #
# -- FROM PALETTABLE -- #
# --------------------- #

logging.info(f"Analyzing '{THIS_RESRC}' source code.")

nbtest = 0

for subdir in sorted(RESRC_DIR.glob("*")):
    if not subdir.is_dir():
        continue

    logging.info(
        f"Working on '{PALETTABLE_SUB_FOLDERS[subdir.name]}' source code."
    )

    pals = extract(subdir)

    resrc_pals_json = subdir.name.replace(' ', '-').upper()
    resrc_pals_json = REPORT_DIR / f"RESRC-PALS-{resrc_pals_json}.json"

    logging.info(f"'{resrc_pals_json.relative_to(PROJ_DIR)}' update.")

    resrc_pals_json.write_text(
        json_dumps(pals)
    )
