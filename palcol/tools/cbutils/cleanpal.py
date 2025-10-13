
#!/usr/bin/env python3

from enum import Enum


TAG_EQUAL_TO = "isequalto"

class PAL_STATUS(Enum):
    IS_NEW   = 1
    EQUAL_TO = 2


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
    status, xtra = PAL_STATUS.IS_NEW, None

    if palettes:
        for n, p in palettes.items():
            if p == candidate:
                status, xtra = PAL_STATUS.EQUAL_TO, n

                break

    match status:
        case PAL_STATUS.IS_NEW:
            palettes[name] = candidate

            logcom.info(f"'{name}' added.")

        case PAL_STATUS.EQUAL_TO:
            ignored[TAG_EQUAL_TO][xtra].append(name)

            logcom.warning(
                f"'{name}' ignored - Equal to '{xtra}'."
            )

    return palettes, ignored
