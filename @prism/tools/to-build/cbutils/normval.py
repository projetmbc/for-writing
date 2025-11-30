#!/usr/bin/env python3

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


def stdname(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    parts = [_capitalize(p) for p in parts if p]

    name = "".join(parts)

    return name


# ----------- #
# -- FLOAT -- #
# ----------- #

def stdfloat(
    x        : float,
    precision: float
) -> float:
    return floor(x * precision) / precision
