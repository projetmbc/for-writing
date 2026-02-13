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

import matplotlib.pyplot as plt
import numpy as np


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_MPL_COLORMAP_BRACES_LISTED = re.compile(
    r'^(\w+)'
    r'\s*=\s*'
    r'(\[\s*\[.*?\]\s*\])',
    re.DOTALL | re.MULTILINE
)

PATTERN_MPL_COLORMAP_BRACES = re.compile(
    r'^_([a-zA-Z0-9_]+)_data'
    r'\s*=\s*'
    r'(\(\s*\(\s*[0-9\s\.,\(\)]*\s*\))',
    re.MULTILINE
)

PATTERN_MPL_COLORMAP_HOOKS = re.compile(
    r'^_([a-zA-Z0-9_]+)_data'
    r'\s*=\s*'
    r'(\{.*?\})',
    re.DOTALL | re.MULTILINE
)

PATTERN_MPL_COLORMAP_DATA_NAME = re.compile(
    r'^_([a-zA-Z0-9_]+)_data\s*=',
    re.MULTILINE
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[2]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"{RESRC_PALS_JSON}.json"


_MPL_CODE_LISTED = RESRC_DIR / "_cm_listed.py"
MPL_CODE_LISTED  = _MPL_CODE_LISTED.read_text()

_MPL_CODE = RESRC_DIR / "_cm.py"
MPL_CODE  = _MPL_CODE.read_text()

# -- DEBUG - ON -- #
#
# URL extraction!
#
# url_pattern = re.compile(r'https?://\S+')

# for line in MPL_CODE.split('\n'):
#     line = line.strip()

#     if (
#         line.startswith('#')
#         and
#         url_pattern.search(line)
#     ):
#         print(line)

# exit()
# -- DEBUG - OFF -- #

# We remove final comments! Some are in data.
MPL_CODE = re.sub(
    r'#.*$', '',
    MPL_CODE,
    flags = re.MULTILINE
)


# ----------- #
# -- TOOLS -- #
# ----------- #

def has_uniformed_steps(steps: list[float]) -> bool:
    diffs = {
        round(
            steps[i + 1] - steps[i],
            PAL_PRECISION
        )
        for i in range(len(steps)-1)
    }

    return len(diffs) == 1


# --------------------- #
# -- FROM MATPLOTLIB -- #
# --------------------- #

logging.info(f"Analyze '{THIS_RESRC}' source code")

pals = dict()


# -- HARD CODED COLOR MAPS -- #

# The easy part.
for match in PATTERN_MPL_COLORMAP_BRACES_LISTED.finditer(MPL_CODE_LISTED):
    palname = match.group(1)
    palname = palname[1:].replace('_data', '')

    stdname = get_stdname(palname)

    paldef = eval(match.group(2))

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind  = '',
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )

# Special case of twilight_shifted_data.
pal_twilight = pals['Twilight'][TAG_RGB_COLS]

paldef = (
      pal_twilight[len(pal_twilight)//2:]
    + pal_twilight[:len(pal_twilight)//2]
)

paldef.reverse()

pals['TwilightShifted'] = resrc_std_palette(
    palname   = 'twilight_shifted',
    palkind  = '',
    paldef    = paldef,
    precision = PAL_PRECISION + 2,
)

# "Brace" coded palettes.
for match in PATTERN_MPL_COLORMAP_BRACES.finditer(MPL_CODE):
    palname = match.group(1)
    stdname = get_stdname(palname)

    paldef = eval(match.group(2))

    if not all(
        isinstance(x, float)
        for c in paldef
        for x in c
    ):
        continue


    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind  = '',
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )

# Old-style coded palettes.
for match in PATTERN_MPL_COLORMAP_HOOKS.finditer(MPL_CODE):
    palname = match.group(1)
    stdname = get_stdname(palname)

# + Palette def?
    try:
        paldef = eval(match.group(2))

    except Exception as e:
        continue

# + RGB same length defs?
    lenghts = set(
        len(d)
        for d in paldef.values()
    )

    if len(lenghts) != 1:
        continue

    common_len = lenghts.pop()

# + No RGB jump?
    if not all(
        y == yy
        for d in paldef.values()
        for x, y, yy in d
    ):
        continue

# + Uniform steps?
    if common_len != 2:
        is_uniform = True

        for d in paldef.values():
            is_uniform &= has_uniformed_steps([
                x[0]
                for x in d
            ])

        if not is_uniform:
            continue

# + A new def.
    cols = {}

    for k in [
        'red',
        'green',
        'blue'
    ]:
        cols[k] = [
            x[1]
            for x in paldef[k]
        ]

    paldef = []

    for i in range(common_len):
        paldef.append([
            cols[k][i]
            for k in [
                'red',
                'green',
                'blue'
            ]
        ])

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind  = '',
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )

# -- COMPUTED COLOR MAPS -- #

# For the remaining palettes that are computed, we adopted
# a hybrid approach by relying on matplotlib to produce a
# 256-color high-resolution palette.
for match in PATTERN_MPL_COLORMAP_DATA_NAME.finditer(MPL_CODE):
    palname = match.group(1)
    stdname = get_stdname(palname)

    if stdname in pals:
        continue

    cmap = plt.get_cmap(palname)

    paldef = cmap(np.linspace(0, 1, 256))

    paldef = [
        [round(float(c), PAL_PRECISION) for c in rgb[:3]]
        for rgb in paldef
    ]

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind  = '',
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )


# ------------------------------- #
# -- CATEGORY FROM SOURCE CODE -- #
# ------------------------------- #

for stdname, infos in pals.items():
    if (
        stdname.startswith('Petroff')
        or
        stdname.startswith("Okabe")
        or
        stdname == "Wistia"
    ):
        pals[stdname][TAG_KIND] = TAG_COLORBLIND

    elif stdname == "Coolwarm":
        pals[stdname][TAG_KIND] = TAG_DIVERGENT


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"Update '{RESRC_PALS_JSON.relative_to(PROJ_DIR)}'")

pals = get_sorted_dict(pals)

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
