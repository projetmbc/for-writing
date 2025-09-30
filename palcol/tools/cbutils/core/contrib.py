#!/usr/bin/env python3

from collections import defaultdict
from pathlib     import Path

from yaml import safe_load

from cbutils.core.logconf  import *
from cbutils.core.messages import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

TAG_CONTRIB_DIR = "contrib"

TAG_STATUS = "status"
TAG_OK     = "ok"


# ----------------------- #
# -- ACCEPTED CONTRIB. -- #
# ----------------------- #

###
# prototype::
#     project_dir : the path of the project folder.
#
#     :return: the key are folders containing accpeted contributions,
#              and values are list of file or folder names.
#
# caution::
#     It is the responsibility of the user code to optimise the paths
#     for humanly useful rendering.
###
def get_accepted_paths(project_dir: Path) -> dict[Path, str]:
    logging.info("Looking for accepted contribs.")

    contrib_dir    = project_dir / TAG_CONTRIB_DIR
    accepted_paths = defaultdict(list)

    for yaml_file in contrib_dir.rglob("status/*.yaml"):
        statusdata = safe_load(yaml_file.read_text())

        if statusdata[TAG_STATUS] != TAG_OK:
            continue

        locdir = yaml_file.parent.parent
        stem   = yaml_file.stem

# Acceptable folder?
        is_folder = (locdir / stem).is_dir()

# Acceptable files?
        files = [
            p
            for p in locdir.glob(f"*/{stem}.*")
            if p.is_file() and p.parent.name != TAG_STATUS
        ]

# Nothing found.
        if not(is_folder or files):
            log_raise_error(
                exception = IOError,
                desc      = f"No contrib. found for '{stem}'.",
            )

# Ambiguity?
        if (
            is_folder and files
            or
            len(files) > 1
        ):
            desc = "Several acceptable contribs."

            xtra = []

            if is_folder:
                xtra.append('One folder.')

            for p in files:
                xtra.append(f"File: '{p.name}'.")

            xtra = f'\n{TAB_ITEM_1}' + TAB_ITEM_1.join(xtra)

            log_raise_error(
                exception = IOError,
                desc      = desc,
                xtra      = xtra,
            )

# Contrib. found.
        path = parent / stem if is_folder else files[0]

        accepted_paths[path.parent].append(path.name)

# Our job is finished.
    return accepted_paths


# ------------------- #
# -- (E)XTRA FILES -- #
# ------------------- #

###
# prototype::
#     file : a \contrib file.
#
#     :return: the list of possible extra files associated to the \contrib file.
#
#
# note::
#     Additional files must have names prefixed by the given file. Here are some examples.
#
#         + path::''my_script_cgf.yaml'' is an aditional file for
#         path::''my_script.py''.
#
#         + path::''my_cfg_tool.py'' is an aditional file for
#         path::''my_cfg.yaml''.
#
#         + path::''my_tool.py'' is not an aditional file for
#         path::''my_cfg.toml''.
###
def get_xtra_files(file: Path) -> list[Path]:
    xtra_files = [
        p
        for p in file.parent.glob(
            f"{file.stem}-*"
        )
        if p != file
    ]

    return xtra_files
