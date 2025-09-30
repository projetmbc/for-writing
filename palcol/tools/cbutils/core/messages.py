#!/usr/bin/env python3

from cbutils.core.logconf import *


# ----------------------- #
# -- STANDARD MESSAGES -- #
# ----------------------- #

###
# prototype::
#     title : a title.
#     desc  : a short description.
#
#     :return: a message with the title highlighted, followed
#              by the description provided.
###
def msg_title(
    title: str,
    desc : str,
) -> str:
    return f"{title.upper()} - {desc}"


###
# prototype::
#     context : context in which codes are created or updated.
#     upper   : set to ''True'', the context is printed in uppercase;
#               otherwise, no case changes are made.
#     several : set to ''True'', this indicates that several codes
#               are involved; otherwise, only one is processed.
#
#     :return: a message indicating the creation or update of files
#              in the given context.
###
def msg_creation_update(
    context: str,
    upper  : bool = True,
    several: bool = False,
) -> str:
    if upper:
        context = context.upper()

    plurial = 's' if several else ''

    return f"{context} code{plurial}: creation or update."


# ---------------------- #
# -- SPECIAL MESSAGES -- #
# ---------------------- #

###
# prototype::
#     context   : the context in which an error is raised and logged.
#     desc      : the descritpion of the error.
#     exception : the \python exception to use.
#     xtra      : an extra text only print when raising the \python
#                 exception.
#
#     :action: log an error and raise an exception.
###
def log_raise_error(
    context  : str,
    desc     : str,
    exception: Exception,
    xtra     : str = '',
) -> None:
    logging.error(
        msg_title(
            title = context,
            desc  = desc
        )
    )

    if xtra:
        xtra = f" {xtra}"

    raise exception(f"{desc}{xtra}")
