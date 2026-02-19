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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_COMMON_PYDEF = re.compile(
    r'_?([A-Z0-9_]+)\s*=\s*(\[[\s\S]*?\n\])'
)

PATTERN_KIND = re.compile(
    r"_PALETTE_TYPE\s*=\s*['\"]([^'\"]+)['\"]"
)

PATTERN_KIND_UNSTD = re.compile(
    r"^_?palette_type\s*=\s*(['\"])(.*?)\1",
    re.MULTILINE
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

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[1]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


# ----------- #
# -- TOOLS -- #
# ----------- #

# -- SPECIAL PALETTABLE SPECS -- #

def extract_kind_unstd(code: str) -> str:
    match = PATTERN_KIND_UNSTD.search(code)

    palkind = match.group(2) if match else ''

    return palkind


def extract_cubehelix(folder: Path) -> dict[str, PaletteCols]:
    _src_code = folder / f"{folder.name}.py"
    src_code = _src_code.read_text()

    palkind = extract_kind_unstd(src_code)

    for d in [
        'palette_rgb',
        '=',
    ]:
        _ , _ , src_code = src_code.partition(d)

    src_pals, _ , _ = src_code.partition('class Cubehelix')

    src_pals = eval(src_pals.strip())

    pals = {}

    for palname, cols in src_pals.items():
        if not palname.endswith('_16'):
            print(name)
            BUG_TODO

        palname = palname[:-3]
        stdname = get_stdname(palname)

        pals[stdname] = resrc_std_palette(
            palname   = palname,
            palkind   = palkind,
            paldef    = pal255_to_pal01(cols),
            precision = PAL_PRECISION + 2,
        )

    return pals


def extract_tableau(folder: Path) -> dict[str, PaletteCols]:
    _src_code = folder / f"{folder.name}.py"
    src_code = _src_code.read_text()

    palkind = extract_kind_unstd(src_code)

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
        palname, _ , pal_size = name.partition('_')

        stdname = get_stdname(palname)

        pal_size = int(pal_size)

        if pal_size > last_sizes[stdname]:
            last_sizes[stdname] = pal_size

            pals[stdname] = resrc_std_palette(
                palname   = palname,
                palkind   = palkind,
                paldef    = pal255_to_pal01(cols),
                precision = PAL_PRECISION + 2,
            )

    return pals


def extract_wesanderson(folder: Path) -> dict[str, PaletteCols]:
    _src_code = folder / f"{folder.name}.py"
    src_code = _src_code.read_text()

    palkind = extract_kind_unstd(src_code)

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

    for palname, cols in src_pals.items():
        stdname = get_stdname(palname)

        cols = cols['colors']

        pals[stdname] = resrc_std_palette(
            palname   = palname,
            palkind   = palkind,
            paldef    = pal255_to_pal01(cols),
            precision = PAL_PRECISION + 2,
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
        get_stdname(kind_and_names[n][1]): resrc_std_palette(
            palname   = kind_and_names[n][1],
            palkind  = kind_and_names[n][0],
            paldef    = p,
            precision = PAL_PRECISION + 2,
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
        logging.info(f"No extraction")

    return pals


# --------------------- #
# -- FROM PALETTABLE -- #
# --------------------- #

logging.info(f"Source - Analyze '{THIS_RESRC}'")

nbtest = 0

_sub_folders = RESRC_SUBDIR_NAME[TAG_PALETTABLE]

for subdir in sorted(RESRC_DIR.glob("*")):
    if not subdir.is_dir():
        continue

    sub_name = subdir.name.upper()

    if not sub_name in _sub_folders:

        TODO

    logging.info(
        f"Subfolder - Work on '{sub_name}'"
    )

    pals = extract(subdir)

    resrc_pals_json = REPORT_DIR / f"{sub_name}.json"

    logging.info(f"JSON - Update '{resrc_pals_json.relative_to(PROJ_DIR)}'")

    pals = get_sorted_dict(pals)

    resrc_pals_json.write_text(
        json_dumps(pals)
    )
