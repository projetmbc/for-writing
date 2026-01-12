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
