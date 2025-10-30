#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent


TRANSLATE_DIR = PROJECT_DIR / "contrib" / "translate"
EN_MANUAL_DIR = TRANSLATE_DIR / "en" / "manual"


PRODUCTS_DIR = PROJECT_DIR / "products"


PAL_JSON_FILE = PRODUCTS_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


CMD_VALS = {
    "palSize": len(ALL_PALETTES['GeoRainbow']),
    "palNb"  : len(ALL_PALETTES),
}


# --------------------- #
# -- DOC - SEARCHING -- #
# --------------------- #

logging.info(
    "Updating English doc (data about palettes)."
)

tex_cfg_file = EN_MANUAL_DIR / "preamble.cfg.sty"

content = tex_cfg_file.read_text()
content = content.strip()

for cmd, val in CMD_VALS.items():
    content = re.sub(
        r'(\\newcommand\\' + cmd + r'\{)(\d+)\}',
        r'\g<1>' + str(val) + '}',
        content
    )

content += "\n"

tex_cfg_file.write_text(content)
