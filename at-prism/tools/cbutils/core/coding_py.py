#!/usr/bin/env python3

import ast
import sys
import re


import                            importlib.util
from   importlib.machinery import ModuleSpec

from black import (
    FileMode,
    format_file_in_place,
    format_str,
    WriteBack,
)


from cbutils.core.coding   import *
from cbutils.core.logconf  import *
from cbutils.core.messages import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

TAG_INIT     = "__init__"
INIT_FILE    = f"{TAG_INIT}.py"

SHEBANG_PYTHON = "#!/usr/bin/env python3\n"


PATTERN_LEGAL_NAME = re.compile(
    r'^[A-Za-z _.-][A-Za-z0-9 _.-]*$',
# We do not accept unicode characters!
    flags = re.ASCII
)

PATTERN_PYSUGLIFY = re.compile(r'[\s\-\.]+')


PATTERNS_HEADERS = [
    PATTERN_COMMENT_HD_1:= re.compile(
        r"#\s+-+\s+#\n# --(.*)-- #\n# -+ #\n"
    ),
    # PATTERN_COMMENT_HD_2:= re.compile(
    #     r"# ~~(.*)~~ #\n"
    # ),
]


# ------------ #
# -- TYPING -- #
# ------------ #

type DictSplittedCode = dict[str, Path]

type LegalSigns = dict[
    str,
    tupe[
        bool,
        list[set[str]]
    ]
]

# ----------------------- #
# -- BUILD PYTHON CODE -- #
# ----------------------- #

###
# prototype::
#     module_name : the name of the module from the \python point
#                   of view (see ''__name__'')
#     file_path   : the path of a \python file.
#
#     :return: a virtual module that allows to work with the code
#              contained in the file specified as an \arg.
#
#
# src::
#     url = https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
###
def import_from_path(
    module_name: str,
    file_path  : str | Path
) -> ModuleSpec:
    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# ----------------------- #
# -- BUILD PYTHON CODE -- #
# ----------------------- #

###
# prototype::
#     name : a name using \ascii letters, digits, spaces, hyphens,
#            underscores and points (no unicode characters accepted).
#
#     :return: a legal \python name.
###
def pysuglify(name: str) -> str:
    if PATTERN_LEGAL_NAME.fullmatch(name) is None:
        raise ValueError(
             "'name' can only use ASCII letters, spaces, hyphens,"
             "digits, underscores and points (no unicode characters)."
            f"See:\n{name}"
        )

    return PATTERN_PYSUGLIFY.sub('_', name)


###
# prototype::
#     folder : a folder path.
#
#     :action: add an path::''init__.py'' file to the folder if one
#              does not already exist.
###
def add_missing_init(folder: Path) -> None:
    initfile = folder / INIT_FILE

    if not initfile.is_file():
        initfile.touch()
        initfile.write_text(SHEBANG_PYTHON)

        logging.info(
            f"'{folder.name}/{INIT_FILE}' file added."
        )


###
# prototype::
#     code : a \python code.
#     file : a file path.
#
#     :action: creation of the file with the \python code given as
#              a parameter as its content, formatted by the \black
#              package.
###
def add_black_pyfile(
    code: Path,
    file: Path
) -> None:
    file.write_text(code)

    format_file_in_place(
        file,
        fast       = False,
        mode       = FileMode(),
        write_back = WriteBack.YES,
    )


###
# prototype::
#     code    : :see: add_black_pyfile
#     file    : :see: add_black_pyfile
#     nbempty : the number of empty lines added before the code
#               that will be added.
#
#     :action: append to the file the \python code formatted by the
#              \black package.
###
def append_black_pyfile(
    code   : Path,
    file   : Path,
    nbempty: int = 1
) -> None:
    code = format_str(
        code,
        mode = FileMode()
    )
    code = '\n' * nbempty + code
    code = file.read_text() + code

    file.write_text(code)


# ------------------------- #
# -- ANALYZE PYTHON CODE -- #
# ------------------------- #

###
# prototype::
#     file        : the \python file to analyse.
#     legal_signs : a dictionary whose keys correspond to function
#                   names and whose values are pairs ''(is_mandatory,
#                   authorised_signs)'' indicating whether the
#                   function must be present and what its possible
#                   signatures are (use of a list of sets of \arg
#                   names).
#     ctxt        : the current context.
#     desc        : short \desc to complement the ''ctxt'' \arg.
#     code        : set to ''None'', this \arg requests that the
#                   entire file code be used; otherwise, the ''code''
#                   value is used (this allows only a useful part of
#                   the file to be analysed).
#
#     :action: verify that special functions have an authorised
#              signature (see the \arg ''legal_signs'').
#
#
# note::
#     Here is a possible value ofr the special \arg ''legal_signs''.
#
#     python::
#         LEGAL_SIGNS = {
#             'parse'   : (
#                 True,
#                 [set(['data']),
#                  set(['amdata_cls', 'data'])]
#             ),
#             'map_list': (
#                 False,
#                 [set(['data_list']),
#                  set(['amdata_cls', 'data_list'])]
#             ),
#         }
###
def validate_signatures(
    file       : Path,
    legal_signs: LegalSigns,
    ctxt       : str,
    desc       : str,
    code       : str | None,
) -> None:
    if code is None:
        code = file.read_text()

    for func_name, (
        is_mandatory,
        authorised_signs
    ) in legal_signs.items():
        sign = get_parse_signature(
            code         = code,
            func_name    = func_name,
            is_mandatory = is_mandatory,
        )

        if sign is None:
            continue

        if not sign in authorised_signs:
            if len(authorised_signs) == 1:
                helper = ["One authorised signature."]

            else:
                helper = ["Authorised signatures."]

            helper += [
                f"  + {func_name}({', '.join(sorted(s))})" for s in authorised_signs
            ]

            helper = '\n'.join(helper)

            sign = f"({', '.join(sorted(sign))})"

            log_raise_error(
                context = ctxt,
                desc    = (
                    f"{desc}: "
                    f"unauthorised signature '{sign}' for "
                    f"'{func_name}' function in file: "
                    f"'{file}'"
                ),
                exception = ValueError,
                xtra      = f"\n\n{helper}",
            )


###
# prototype::
#     code         : a \python code.
#     func_name    : a \func name.
#     is_mandatory : set to ''False'', this indicates to return
#                    ''None'' if no \func has the given name;
#                    otherwise, a ''ValueError'' is raised.
#
#     :return: the set of its \args in case of success; otherwise,
#              see the \desc of the \arg ''ignore_error''.
###
def get_parse_signature(
    code        : str,
    func_name   : str,
    is_mandatory: bool = True,
) -> set[str] | None:
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and
            node.name == func_name
        ):
            args = set(arg.arg for arg in node.args.args)

# Not use but useful to get the default values.
#             for i, default in enumerate(
#                 node.args.defaults,
#                 start = len(args) - len(node.args.defaults)
#             ):
#                 args[i] += f"={ast.unparse(default)}"

            return args

    if is_mandatory:
        raise ValueError(
            f"Missing '{func_name}' function in the code."
        )


# ------------------------- #
# -- EXTRACT PYTHON CODE -- #
# ------------------------- #

###
# prototype::
#     file        : a file to normalize.
#     hds_ignored : a list of header titles to ignore some sections.
#
#     :return: the code of the file without the unwanted section contents.
###
def finalize_pycode(
    file       : Path,
    hds_ignored: list[str]
) -> str:
    code = []

    for header, content in hd_split_pyfile(file).items():
        if header in hds_ignored:
            continue

        code.append(
            f"""
{magic_comment(header)}

{content}
            """.strip()
        )

    code = '\n\n\n'.join(code) + '\n'

    return code


###
# prototype::
#     file : :see: ./coding.hd_split_file
#
#     :return: :see: ./coding.hd_split_file
#
#
# Here is a fictive content with the singme kind of section available.
#
# python::
#     ...
#
#     # ------------- #
#     # -- TITLE 1 -- #
#     # ------------- #
#
#     ...
#
#     # ------------- #
#     # -- TITLE 2 -- #
#     # ------------- #
#
#     ...
###
def hd_split_pyfile(file: Path) -> DictSplittedCode:
    return hd_split_file(
        file        = file,
        pat_headers = PATTERNS_HEADERS,
    )


###
# prototype::
#     title : a title
#
#     :return: the level 1 magic comment for a section title.
###
def magic_comment(title: str) -> str:
    if title == TAG_ROOT_HEADER:
        return ""

    title = f"-- {title} --"
    rule  = '-'*len(title)

    title = f"""
# {rule} #
# {title} #
# {rule} #
    """.strip()

    return title
