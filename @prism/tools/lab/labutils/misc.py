#!/usr/bin/env python3

# --------------------------- #
# -- NAME AND SOURCE - UID -- #
# --------------------------- #

TAG_uid_SEP = '::'


def extract_name_n_srcname(
    name_srcname: str
) -> (str, str):
    return tuple(name_srcname.split(TAG_uid_SEP))


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return TAG_uid_SEP.join([name, srcname])
