#!/usr/bin/env python3

from pathlib import Path

from cbutils.core.logconf import *


# ------------------------------ #
# -- CREATION, DELETION & CO. -- #
# ------------------------------ #

###
# prototype::
#     folder : a folder path.
#
#     :action: if the directory with the path specified doesn't
#              exist, it is created.
###
def add_missing_dir(folder : Path) -> None:
    if not folder.is_dir():
        folder.mkdir(
            parents  = True,
            exist_ok = True
        )

        logging.warning(f"Folder added: '{folder}'")


###
# prototype::
#     folder : a folder path.
#
#     :action: an empty directory with the path specified as
#              a parameter is obtained at the end of the process
#              (if the folder does not exist, it will be created).
###
def empty_dir(folder : Path) -> None:
# A folder to create.
    if not folder.is_dir():
        add_missing_dir(folder)

# A folder to empty.
    else:
        logging.warning(f"Emptying folder: '{folder}'")

# ''top_down=False'' is for visiting subdirectories first, then
# the parent. Here, tis is required because files must be deleted
# before their parent dirs.
        for root, dirs, files in folder.walk(top_down = False):
# No file must be left.
            for name in files:
                (root / name).unlink()

# The empty dirs are now removable.
            for name in dirs:
                (root / name).rmdir()


###
# prototype::
#     file    : a file path.
#     content : content of the file.
#
#     :action: the file with the content expected is created.
###
def create_update_file(
    file     : Path,
    content  : str,
    log_level: str = TAG_INFO
) -> None:
    LOG_PRINTERS[log_level](f"Creation or update: '{file.name}'.")

    file.touch()
    file.write_text(content)
