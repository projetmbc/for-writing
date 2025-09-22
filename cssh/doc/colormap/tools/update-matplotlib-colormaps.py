from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.cm     as cm

sample_size = 10
scale_factor = sample_size - 1

THIS_DIR         = Path(__file__).parent
COLORMAP_DOC_DIR = THIS_DIR.parent
GALLERY_DIR      = COLORMAP_DOC_DIR / "gallery"

TEMPLATE_FILE    = COLORMAP_DOC_DIR / "template" / "model.tex"
LUA_CFG_FILE     = COLORMAP_DOC_DIR / "common" / "colormap.lua"

print("Working on the matplotlib color maps.")

lua_code = []

allnames = sorted(
    [
        cm for cm in plt.colormaps()
        if cm[-2:] != "_r"
    ],
    key = lambda x: x.lower()
)

for cmap_name in allnames:
    cmap      = cm.get_cmap(cmap_name)
    cmap_name = cmap_name[0].upper() + cmap_name[1:]

    colors = [
        f"{{{','.join(f"{v:.4f}" for v in list(cmap(i / scale_factor))[:-1])}}}"
        for i in range(sample_size)
    ]

    print(f" + {cmap_name}")

    lua_code.append(f"pal{cmap_name} = {{{','.join(colors)}}}")

print( "   ---")
print(f" + {len(allnames)} ''direct'' color maps found.")

lua_code = "\n".join(lua_code)

LUA_CFG_FILE.write_text(lua_code)
