#!/usr/bin/env python3

from enum import Enum

import numpy as np

from .normval import stdfloat

PALSIZE   = 10  # <--- CSS and manual uses.
PRECISION = 10**6
TOLERANCE = 10**(-5)

class PAL_STATUS(Enum):
    IS_NEW     = 1
    EQUAL_TO   = 2
    REVERSE_OF = 3

STATUS_MSG = {
    PAL_STATUS.IS_NEW    : "Is new",
    PAL_STATUS.EQUAL_TO  : "Equal to",
    PAL_STATUS.REVERSE_OF: "Reverse of",
}

STATUS_TAG = {
    i: m.lower().replace(' ', '-')
    for i, m in STATUS_MSG.items()
}


TAG_CTXT = 'context'

TAG_SCICOLMAP = "Scientific Colour Maps"
TAG_APRISM    = "@prism"
TAG_MPL       = "Matplotlib"






def minimize_palette(p: list[float]) -> list[float]:
    if len(set(tuple(c) for c in p)) == len(p):
        return p

    new_p = []

    for c in p:
        if (not new_p or c != new_p[-1]):
            new_p.append(c)

    return new_p


def equalfloatlist(
    list_1: list[ [float, float, float] ],
    list_2: list[ [float, float, float] ]
) -> bool:
    if len(list_1) != len(list_2):
        return False

    for triplet_1, triplet_2 in zip(list_1, list_2):
        for a, b in zip(triplet_1, triplet_2):
            if abs(a - b) > TOLERANCE:
                return False

    return True


def update_palettes(
    context  : str,
    name     : str,
    candidate: list[ [float, float, float] ],
    palettes : dict[ str, list[ [float, float, float] ] ],
    ignored  : dict[ str, dict[ str, [str] ] ],
    logcom
) -> (
    dict[ str, list[ [float, float, float] ] ],
    dict[ str, dict[ str, [str] ] ]
):
    status = PAL_STATUS.IS_NEW

    if palettes:
        for n, p in palettes.items():
            if equalfloatlist(candidate, p):
                status   = PAL_STATUS.EQUAL_TO
                lastname = n

                break

            elif equalfloatlist(candidate, p[::-1]):
                status   = PAL_STATUS.REVERSE_OF
                lastname = n

                break

    match status:
        case PAL_STATUS.IS_NEW:
            palettes[name] = norm_palette(candidate)

            logcom.info(f"'{name}' added.")

        case _:
            ignored[name] = {
                STATUS_TAG[status]: lastname,
                TAG_CTXT          : context
            }

            logcom.warning(
                f"'{name}' ignored - {STATUS_MSG[status]} '{lastname}'."
            )

    return palettes, ignored



def norm_palette(
    palette: list[ [float, float, float] ]
) -> list[ [float, float, float] ]:
    size = len(palette)

    pal_array = np.array(palette)

    linspace_pal    = np.linspace(0, 1, size)
    linspace_target = np.linspace(0, 1, PALSIZE)

    r_vals = pal_array[:, 0]
    g_vals = pal_array[:, 1]
    b_vals = pal_array[:, 2]

    r_interpo = np.interp(linspace_target, linspace_pal, r_vals)
    g_interpo = np.interp(linspace_target, linspace_pal, g_vals)
    b_interpo = np.interp(linspace_target, linspace_pal, b_vals)

    # Reconstruction des vecteurs RGB
    result = [
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

    return result
