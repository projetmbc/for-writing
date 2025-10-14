
#!/usr/bin/env python3

from enum import Enum


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
            palettes[name] = candidate

            logcom.info(f"'{name}' added.")

        case _:
            ignored[STATUS_TAG[status]][lastname].append(name)

            logcom.warning(
                f"'{name}' ignored - {STATUS_MSG[status]} '{lastname}'."
            )

    return palettes, ignored
