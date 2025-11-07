<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


Add new products to @prism
==========================

**Table of contents**

<a id="MULTIMD-GO-BACK-TO-TOC"></a>
- [Structure of the contrib/products folder](#MULTIMD-TOC-ANCHOR-0)
- [How to propose new palettes?](#MULTIMD-TOC-ANCHOR-1)
    - [Folder organization](#MULTIMD-TOC-ANCHOR-2)
    - [The dev folder](#MULTIMD-TOC-ANCHOR-3)
    - [The palettes folder](#MULTIMD-TOC-ANCHOR-4)
    - [The status folder](#MULTIMD-TOC-ANCHOR-5)
    - [The extend.py file](#MULTIMD-TOC-ANCHOR-6)
    - [The fake-prod folder](#MULTIMD-TOC-ANCHOR-7)
    - [The readme folder](#MULTIMD-TOC-ANCHOR-8)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
Structure of the contrib/products folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
----------------------------------------

We will briefly explain the following structure of the `contrib/products` folder.

~~~
+ contrib
  + changes
  + luadraw
  + readme
  + status
~~~

Here is how the different folders are used.

1. `changes` is used to communicate changes related to contributions.
2. `readme`, managed by the `@prism` developer, is used to generate the `contrib/products/README.md` file.
3. The other folders are the contributions themselves, the development process for which is explained in the following section.

<a id="MULTIMD-TOC-ANCHOR-1"></a>
How to propose new palettes? <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
----------------------------

For our explanations, we will use the real-world case of the `luadraw` contribution.

<a id="MULTIMD-TOC-ANCHOR-2"></a>
### Folder organization <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The following structure for the `luadraw` folder is mandatory. Only the name `luadraw` can be chosen freely by the contributor: the name must be related to the technology used to produce new palettes.

~~~
+ luadraw
    + readme
    + dev
    + palettes
    + status
    * extend.py
~~~
<a id="MULTIMD-TOC-ANCHOR-3"></a>
### The dev folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is the sole responsibility of the contributor. Its purpose is to provide a simple way to create and test new palettes.

<a id="MULTIMD-TOC-ANCHOR-4"></a>
### The palettes folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is used to store palettes provided as files using the specific implementation chosen. Each file name gives the name of the palette.
For example, on October 14, 2025, the `palettes` folder contained the following items defining three palettes named `BlindFish`, `GasFlame`, and `GroovyRainbow`.

~~~
- palettes
    * BlindFish.lua
    * BurningGrass.lua
    * GasFlame.lua
    * GeoRainbow.lua
    * PastelRainbow.lua
~~~

In this folder, for example, we had the following `BlindFish.lua` file generated mainly by the `extend.py` file, which we will discuss soon.

~~~lua
-- author: Christophe, Bal

-- ludraw definition used.

-- PALETTE = {
--   Gray,
--   SlateGray,
--   LightSkyBlue,
--   LightPink,
--   Pink,
--   LightSalmon,
--   FireBrick,
-- }

PALETTE = {
  {0.502, 0.502, 0.502},
  {0.4392, 0.502, 0.5647},
  {0.5294, 0.8078, 0.9804},
  {1, 0.7137, 0.7569},
  {1, 0.7529, 0.7961},
  {1, 0.6275, 0.4784},
  {0.698, 0.1333, 0.1333}
}
~~~
> ***NOTE.*** *The size of palettes provided by `@prism` is fixed, but nothing prevents you from using any number of colors you wish when creating your own.*

<a id="MULTIMD-TOC-ANCHOR-5"></a>
### The status folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder allows you to know the status of your proposal. Its structure mimics the folder of contributions: `YAML` files correspond to contribution files.

<a id="MULTIMD-TOC-ANCHOR-6"></a>
### The extend.py file <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This file must follow the following template.

~~~python
#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

import ast
import re


# -------------------- #
# -- EXTRACT COLORS -- #
# -------------------- #

###
# prototype::
#     code : a definition of a palette with the technology chosen.
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" \json version
#              of the palette.
###
def parse(code: str) -> list[ [float, float, float] ]:
    ...


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "..."

###
# prototype::
#     credits  : the credits to the ''@prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used.
#
#
# warning::
#     Except if it is totally impossible, the code returned must
#     offer the ability to access a palette via the string name of
#     the variable associated with it.
###
def build_code(
    credits : str,
    palettes: dict[ str, list[ [float, float, float] ] ]
) -> str:
    ...


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    ...
~~~
<a id="MULTIMD-TOC-ANCHOR-7"></a>
### The fake-prod folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is a template used to create the final version of the implementation.
It must contain a palette file named as indicated in `extend.py` (the content of this mandatory file can be fake).

> ***NOTE.*** *A good practice is to provide a folder `showcase` for local testing without installation.*

> ***WARNING.*** *Make sure to leave nothing unnecessary, as the structure will be copied entirely.*

<a id="MULTIMD-TOC-ANCHOR-8"></a>
### The readme folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `README.md` file of the contribution folder is written in small sections in the `readme` folder which has the following mandatory structure. These sections will also be used to produce documentations for the final product.

~~~
- readme
    * about.yaml
    * desc.md
    * how-to-create.md
    * how-to-use.md
    * title.md
~~~

Here is the purpose of each of these files.

1. **`about.yaml` must not be changed.** It gives the way to gather the `MD` files to build the `README.md` file of the specific contribution folder.
2. `title.md` is the title for the specific technology.
3. `desc.md` is a short description of the specific technology.
4. `how-to-create.md` gives the process to follow to create new palettes using the specific technology.
5. `how-to-use.md` explains how to use one of the `@prism` palettes available when working with the specific technology.
