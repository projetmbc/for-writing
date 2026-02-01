#!/usr/bin/env python3

from typing import (
    Annotated,
    Callable,
    Optional,
    TypeAlias, TypedDict,
)


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = Annotated[list[float], 3]
PaletteCols:TypeAlias = list[RGBCols]

class PaletteData(TypedDict):
    metadata: dict[str, str]
    palette : PaletteCols
