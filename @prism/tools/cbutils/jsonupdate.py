#!/usr/bin/env python3

from pathlib import Path

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# ----------- #
# -- TOOLS -- #
# ----------- #

def update_jsons(
    nb_new_pals: int = -1,
    names      : dict[str, str] | None = None,
    jsnames    : Path | None = None,
    credits    : dict[str, str] | None = None,
    jscredits  : Path | None = None,
    reports    : dict[ str, dict[ str, [str] ] ] | None = None,
    jsreports  : Path | None = None,
    palettes   : dict[ str, list[ [float, float, float] ] ] | None = None,
    jspalettes : Path | None = None,
    logcom = None
) -> None:
    if not names is None:
        jsnames.write_text(
            json_dumps(names)
        )

    if credits is None:
        return None

    jscredits.write_text(
        json_dumps(credits)
    )

    jsreports.write_text(
        json_dumps(reports)
    )

    if nb_new_pals != 0:
        logcom.info("Update palette JSON file.")

        jspalettes.write_text(
            json_dumps(palettes)
        )
