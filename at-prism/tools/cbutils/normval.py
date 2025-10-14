
#!/usr/bin/env python3

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

def _capitalize(n):
    return n[0].upper() + n[1:]

def stdname(n):
    letters = set(n)

    if not letters <= CHARS_ALLOWED:
        for c in letters - CHARS_ALLOWED:
            n = ''.join([
                _capitalize(p)
                for p in n.split(c)
            ])

    else:
        n = _capitalize(n)

    return n


# ----------- #
# -- FLOAT -- #
# ----------- #

def stdfloat(
    x        : float,
    precision: float
) -> float:
    return floor(x * precision) / precision


def minimize_palette(p: list[float]) -> list[float]:
    if len(set(tuple(c) for c in p)) == len(p):
        return p

    new_p = []

    for c in p:
        if (not new_p or c != new_p[-1]):
            new_p.append(c)

    return new_p
