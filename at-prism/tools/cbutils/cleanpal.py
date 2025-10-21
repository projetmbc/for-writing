#!/usr/bin/env python3

from enum import Enum

import numpy as np

from .normval import stdfloat

SAMPLING_SIZE = 8
PRECISION     = 10**5

class PAL_STATUS(Enum):
    IS_NEW     = 1
    EQUAL_TO   = 2
    REVERSE_OF = 3



STATUS_MSG = {
    PAL_STATUS.EQUAL_TO  : "Equal to",
    PAL_STATUS.REVERSE_OF: "Reverse of",
}

STATUS_TAG = {
    i: m.lower().replace(' ', '-')
    for i, m in STATUS_MSG.items()
}


def update_palettes(
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
            if p == candidate:
                status   = PAL_STATUS.EQUAL_TO
                lastname = n

                break

            elif p[::-1] == candidate:
                status   = PAL_STATUS.REVERSE_OF
                lastname = n

                break

    match status:
        case PAL_STATUS.IS_NEW:
            palettes[name] = norm_palette(candidate)

            logcom.info(f"'{name}' added.")

        case _:
            ignored[STATUS_TAG[status]][lastname].append(name)

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
    linspace_target = np.linspace(0, 1, SAMPLING_SIZE)

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
