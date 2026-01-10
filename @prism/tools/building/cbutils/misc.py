#!/usr/bin/env python3

from typing import Callable

from enum    import Enum
from pathlib import Path


from .core import msg_creation_update


class TagFileSatus(Enum):
    NO_TAG        = 1
    BAD_TAG_START = 2
    BAD_TAG_END   = 3
    TAG_OK        = 4


TAG_CONTEXT   = 'context'
TAG_FILE_PATH = 'file-path'


def get_tag_status(
    txtfile  : Path,
    tag_start: str,
    tag_end  : str,
) -> TagFileSatus:
    content = txtfile.read_text()

    if not tag_start in content:
        return TagFileSatus.NO_TAG

    for tag in [
        tag_start,
        tag_end,
    ]:
        if content.count(tag) != 1:
            if tag == tag_start:
                return TagFileSatus.BAD_TAG_START

            return TagFileSatus.BAD_TAG_END

    return TagFileSatus.TAG_OK


def tag_update(
    logger         : Callable,
    log_raise_error: Callable,
    txtfile        : Path,
    tag_start      : str,
    tag_end        : str,
    subcontent     : str,
    error_about    : dict = dict(),
    tag_is_optional: bool = True,
) -> None:
# Well-used tags?
    tag_status = get_tag_status(
        txtfile   = txtfile,
        tag_start = tag_start,
        tag_end   = tag_end,
    )

    if tag_status == TagFileSatus.NO_TAG:
        if tag_is_optional:
            return None

        log_raise_error(
            context   = error_about[TAG_CONTEXT],
            desc      = f"missing magic comments.",
            exception = ValueError,
            xtra      = f"See the file:\n'{error_about[TAG_FILE_PATH]}'",
        )

    if tag_status in [
        TagFileSatus.BAD_TAG_START,
        TagFileSatus.BAD_TAG_END
    ]:
        tag = (
            TAG_STRUCT_START
            if tag_status == TagFileSatus.BAD_TAG_START else
            TAG_STRUCT_END
        )

        log_raise_error(
            context   = error_about[TAG_CONTEXT],
            desc      = f"use the following magic comment only once:\n{tag}",
            exception = ValueError,
            xtra      = f"See the file:\n'{error_about[TAG_FILE_PATH]}'",
        )

# A file to update.
    logger.info(
        msg_creation_update(
            context = f"'{error_about[TAG_FILE_PATH]}'",
            upper   = False,
        )
    )

    content = txtfile.read_text()

    before, _ , after = content.partition(f"\n{tag_start}")

    _ , _ , after = after.partition(f"{tag_end}\n")

    content = f"""
{before}
{tag_start}
{subcontent}
{tag_end}
{after}
    """.strip() + '\n'

    txtfile.write_text(content)



def extract_name_n_srcname(name_srcname: str) -> (str, str):
    return tuple(name_srcname.split('::'))


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return '::'.join([name, srcname])


def reverse_build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return build_name_n_srcname(srcname, name)
