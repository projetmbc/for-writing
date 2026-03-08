#!/usr/bin/env python3

from typing import Callable, TypeAlias

from copy import deepcopy
from enum import Enum

import numpy as np

from .constants import *
from .normval   import stdfloat
from .misc      import *


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = [float, float, float]
PaletteCols:TypeAlias = list[RGBCols]


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PALSIZE   = 10  # <--- CSS and manual uses.
PRECISION = 10**6
TOLERANCE = 10**(-5)


class PAL_STATUS(Enum):
    IS_NEW      = 1
    EQUAL_TO    = 2
    REVERSE_OF  = 3
    SAME_NAME   = 4
    SUBSET_OF   = 5
    SHIFT_OF    = 6
    SAME_VISUAL = 7
    REVSHIFT_OF = 8

STATUS_MSG = {
    PAL_STATUS.IS_NEW     : "Is new",
    PAL_STATUS.EQUAL_TO   : "Equal to",
    PAL_STATUS.REVERSE_OF : "Reverse of",
    PAL_STATUS.SAME_NAME  : "Visually identical to",
    PAL_STATUS.SAME_VISUAL: "Same name as",
    PAL_STATUS.SUBSET_OF  : "Subset of",
    PAL_STATUS.SHIFT_OF   : "Shift of",
    PAL_STATUS.REVSHIFT_OF: "Reverse and shift of",
}

STATUS_TAG = {
    i: m.lower().replace(' ', '-')
    for i, m in STATUS_MSG.items()
}


TAG_SAME_NAME     = STATUS_TAG[PAL_STATUS.SAME_NAME]
TAG_NAMES_IGNORED = "names-ignored"
TAG_NEW_NAMES     = "new-names"

TAG_CTXT  = 'context'
TAG_METH  = 'method'
TAG_AUTO  = 'auto'
TAG_HUMAN = 'human'


def norm_float_pal(
    pal: PaletteCols,
    precision: int
) -> PaletteCols:
    new_pal = list(
        list(
            map(
                lambda x: round(x, precision), rgb
            )
        )
        for rgb in pal
    )

    return new_pal


def resrc_std_palette(
    palname  : str,
    palcatego: str,
    paldef   : PaletteCols,
    precision: int
):
    return {
        TAG_ORIGINAL_NAME: palname,
        TAG_CATEGO       : palcatego,
        TAG_RGB_COLS     : norm_float_pal(paldef, precision + 2),
    }


# def minimize_palette(p: PaletteCols) -> PaletteCols:
#     if len(set(tuple(c) for c in p)) == len(p):
#         return p

#     new_p = []

#     for c in p:
#         if (not new_p or c != new_p[-1]):
#             new_p.append(c)

#     return new_p


def equalfloat_palettes(
    list_1: PaletteCols,
    list_2: PaletteCols
) -> bool:
    if len(list_1) != len(list_2):
        return False

    for triplet_1, triplet_2 in zip(list_1, list_2):
        for a, b in zip(triplet_1, triplet_2):
            if abs(a - b) > TOLERANCE:
                return False

    return True


def pal255_to_pal01(pal: PaletteCols) -> PaletteCols:
    new_pal = list(
        (r / 255, g / 255, b / 255)
        for (r, g, b) in pal
    )

    return new_pal


def namectxt(
    name: str,
    ctxt: str
) -> str:
    return f"{name}::{ctxt}"


def extract_namectxt(name_n_ctxt: str) -> (str, str):
    return name_n_ctxt.split('::')


# def update_palettes(
#     context  : str,
#     name     : str,
#     candidate: PaletteCols,
#     palettes : dict[str, PaletteCols],
#     ignored  : dict[str, dict[ str, [str] ] ],
#     logcom   = Callable,
# ) -> (
#     str,
#     dict[str, PaletteCols],
#     dict[ str, dict[ str, [str] ] ]
# ):
#     name_n_ctxt = namectxt(name, context)

# # New name?
#     if name_n_ctxt in ignored[TAG_NEW_NAMES]:
#         _name = name

#         name        = ignored[TAG_NEW_NAMES][name_n_ctxt]
#         name_n_ctxt = namectxt(name, context)

#         logcom.warning(f"'{_name}' changed to '{name}'.")

# # To ignore.
#     if name_n_ctxt in ignored:
#         _meth = ignored[name_n_ctxt][TAG_METH]

#         logcom.warning(f"'{name}' is ignored ({_meth} method).")

#         ignored[TAG_NAMES_IGNORED].append(name)

#         return name, palettes, ignored

# # Name already used or ignored.
#     if (
#         name in palettes
#         or
#         name in ignored[TAG_NAMES_IGNORED]
#     ):
#         prevctxts = ignored[TAG_SAME_NAME].get(name, [])

#         prevctxts.append([
#             context,
#             candidate
#         ])

#         ignored[TAG_SAME_NAME][name] = prevctxts
#         ignored[TAG_NAMES_IGNORED].append(name)

#         logcom.warning(
#             f"'{name}' already used - Human checking needed."
#         )

#         return name, palettes, ignored

# # We have to analyze the palette.
#     candidate = norm_palette(candidate)
#     status    = PAL_STATUS.IS_NEW

#     for n, p in palettes.items():
#         if equalfloat_palettes(candidate, p):
#             status   = PAL_STATUS.EQUAL_TO
#             lastname = n

#             break

#         elif equalfloat_palettes(candidate, p[::-1]):
#             status   = PAL_STATUS.REVERSE_OF
#             lastname = n

#             break

#     match status:
#         case PAL_STATUS.IS_NEW:
#             palettes[name] = norm_palette(candidate)

#             logcom.info(f"'{name}' added.")

#         case _:
#             ignored[name_n_ctxt] = {
#                 STATUS_TAG[status]: lastname,
#                 TAG_METH          : TAG_AUTO,
#             }

#             logcom.warning(
#                 f"'{name}' ignored - {STATUS_MSG[status]} '{lastname}'."
#             )

#     return name, palettes, ignored


def norm_palette(
    palette: PaletteCols,
    maxsize: int,
) -> PaletteCols:
    size = len(palette)

    if size <= maxsize:
        return palette

    pal_array = np.array(palette)

    linspace_pal    = np.linspace(0, 1, size)
    linspace_target = np.linspace(0, 1, maxsize)

    r_vals = pal_array[:, 0]
    g_vals = pal_array[:, 1]
    b_vals = pal_array[:, 2]

    r_interpo = np.interp(linspace_target, linspace_pal, r_vals)
    g_interpo = np.interp(linspace_target, linspace_pal, g_vals)
    b_interpo = np.interp(linspace_target, linspace_pal, b_vals)

    # Reconstruction des vecteurs RGB
    norm_palette = [
        list(
            map(
                lambda x: stdfloat(x, PRECISION),
                [r, g, b]
            )
        )
        for r, g, b in zip(
            r_interpo,
            g_interpo,
            b_interpo
        )
    ]

    return norm_palette


# def resume_nbpals_build(
#     context    : str,
#     nb_new_pals: int,
#     palettes   : dict[str, PaletteCols],
#     logcom
# ) -> int:
#     nb_new_pals = len(palettes) - nb_new_pals

#     if nb_new_pals == 0:
#         logcom.info("Nothing new found.")

#     else:
#         plurial = "" if nb_new_pals == 1 else "s"

#         logcom.info(
#             f"{nb_new_pals} palette{plurial} build from {context}."
#         )

#     return nb_new_pals




def get_pal_alias(
    suffixes    : dict,
    alias_by_src: dict
) -> dict:
    new_palnames = dict()

    for techno, namerules in alias_by_src.items():
        if techno == TAG_SUFFIXES:
            continue

        this_suffix = suffixes[techno]

        suffix_used = ''

        for name, rule in namerules.items():
            if rule == '.':
                newname = f"{name}{this_suffix}"

                suffix_used = this_suffix

            elif '*' in rule:
                newname = rule.replace('*', this_suffix)

                suffix_used = this_suffix

            else:
                newname = rule

            uid = (name, techno)

            assert not uid in new_palnames

            new_palnames[uid] = (newname, suffix_used)

    return new_palnames



def isublistof(pal_1, pal_2):
    cols_1 = deepcopy(pal_1)
    cols_2 = deepcopy(pal_2)

    positions = []
    pos       = -1

    while cols_1:
        c = cols_1.pop(0)

        if not c in cols_2:
            return False, []

        cursor = cols_2.index(c)
        pos   += cursor + 1

        positions.append(pos)

        cols_2 = cols_2[cursor + 1:]

    return True, positions


def isshiftof(pal_1, pal_2):
    if len(pal_1) != len(pal_2):
        return False, -1

    i = pal_2.index(pal_1[0])

    pal_shifted = pal_2[i:] + pal_2[:i]

    if pal_1 != pal_shifted:
        return False, -1

    return True, i + 1


def isreversedshiftof(pal_1, pal_2):
    return isshiftof(pal_1[::-1], pal_2)
