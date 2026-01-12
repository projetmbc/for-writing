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
