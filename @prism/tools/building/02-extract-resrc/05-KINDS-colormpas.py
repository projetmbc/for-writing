#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #



THIS_RESRC = TAG_COLORMAPS


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


THIS_RESRC_DIR = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)




def parse_markdown_palettes(text):
    # 1. Extraire le type de schéma (Titre #)
    type_match = re.search(r'^#\s+(.+)', text, re.MULTILINE)
    schema_type = type_match.group(1).replace(' Schemes', '').strip() if type_match else "Unknown"

    results = {schema_type: {}}

    # 2. Découper par section de projet (Titre ##)
    # On cherche tout ce qui commence par ## jusqu'au prochain ## ou la fin
    sections = re.split(r'\n##\s+', text)

    for section in sections:
        lines = section.strip().split('\n')
        if not lines:
            continue

        project_name = lines[0].strip()

        # Ignorer la section "Table of contents"
        if "Table of contents" in project_name or not project_name:
            continue

        # 3. Extraire les noms des palettes dans les tableaux
        # On cherche les lignes qui commencent par | et qui ne sont pas des en-têtes
        palettes = []
        for line in lines:
            if line.startswith('|') and '---' not in line and 'Name' not in line:
                # On prend le premier élément entre les pipes
                parts = line.split('|')
                if len(parts) > 1:
                    palette_name = parts[1].strip()
                    if palette_name:
                        palettes.append(palette_name)

        if palettes:
            results[schema_type][project_name] = palettes

    return results

# --- Exécution et affichage ---

for mdpath in THIS_RESRC_DIR.glob('docs/*.md'):
    print()
    print(parse_markdown_palettes(mdpath.read_text()))
