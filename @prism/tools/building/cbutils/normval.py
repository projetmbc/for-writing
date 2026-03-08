#!/usr/bin/env python3

from typing import Any

import re

from math   import floor
from string import (
    ascii_letters,
    digits,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CHARS_ALLOWED = set(ascii_letters + digits)


# ------------ #
# -- STRING -- #
# ------------ #

def _capitalize(text: str) -> str:
    return text[0].upper() + text[1:]


def get_stdname(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    parts = [_capitalize(p) for p in parts if p]

    name = "".join(parts)

    return name


def get_nospace_lower(text: str) -> str:
    text = text.replace(' ', '')
    text = text.lower()

    return text


# ----------- #
# -- FLOAT -- #
# ----------- #

def stdfloat(
    x        : float,
    precision: float
) -> float:
    return floor(x * precision) / precision


# ---------- #
# -- DICT -- #
# ---------- #

def get_sorted_dict(
    onedict: dict[str, Any]
) -> dict[str, Any]:
    return {
    k: onedict[k]
    for k in sorted(
        onedict,
        key = lambda x: x.lower()
    )
}


# ----------------- #
# -- HUMAN RANGE -- #
# ----------------- #

TAG_INDICES = 'indices'
TAG_RANGE   = 'range'

def human_range(nbs: list[int]) -> dict[str, str]:
    if len(nbs) <= 3:
        return [(TAG_INDICES, nbs)]

    all_batches = []
    last_batch  = [nbs[0]]

    for i in range(1, len(nbs)):
        if len(last_batch) == 1:
            last_batch.append(nbs[i])

            last_delta = nbs[i] - nbs[i-1]

        else:
            if nbs[i] - nbs[i-1] == last_delta:
                last_batch.append(nbs[i])

            else:
                all_batches.append(last_batch)

                last_batch = [nbs[i]]

    all_batches.append(last_batch)

    data = []

    for batch in all_batches:
        if len(batch) <= 3:
            data.append((
                TAG_INDICES,
                batch
            ))

        else:
            data.append((
                TAG_RANGE,
                [
                    batch[0],          # Start
                    batch[-1],         # End
                    batch[1] - batch[0]  # Step
                ]
            ))

    return data
