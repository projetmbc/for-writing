#!/usr/bin/env python3

# --------------------------- #
# -- NAME AND SOURCE - UID -- #
# --------------------------- #

TAG_NSN_SEP = '::'


def extract_name_n_srcname(
    name_srcname: str
) -> (str, str):
    return tuple(name_srcname.split(TAG_NSN_SEP))


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return TAG_NSN_SEP.join([name, srcname])
