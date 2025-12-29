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
    - [The tests folder](#MULTIMD-TOC-ANCHOR-4)
    - [The palettes folder](#MULTIMD-TOC-ANCHOR-5)
    - [The status folder](#MULTIMD-TOC-ANCHOR-6)
    - [The extend.py file](#MULTIMD-TOC-ANCHOR-7)
    - [The fake-prod folder](#MULTIMD-TOC-ANCHOR-8)
    - [The readme folder](#MULTIMD-TOC-ANCHOR-9)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
Structure of the contrib/products folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
----------------------------------------

We will briefly explain the following structure of the `contrib/products` folder.

~~~
+ contrib
  + changes
  + css
  + latex
  + lua
  + readme
  + status
  + template-stucture
~~~

Here is how the different folders are used.

1. `changes` is used to communicate changes related to contributions.
2. `readme`, managed by the `@prism` developer, is used to generate the `contrib/products/README.md` file.
3. `status`, managed by the `@prism` developer, contains `YAML` files indicating whether an implementation has been accepted or not, along with the reason for this status. ***No coding skill is needed to read these `YAML` files.***
4. `template-structure` provides a starting structure for adding new implementations.
5. The other folders are the contributions themselves, the development process for which is explained in the following section.

<a id="MULTIMD-TOC-ANCHOR-1"></a>
How to propose new palettes? <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
----------------------------

For our explanations, we will use the real-world case of the `lua` contribution.

> ***CAUTION.*** *Only the folders `dev` (for creation) and `palettes` (for submission) are used for palette creation. Don't modify any other folders unless you're the maintainer.*

<a id="MULTIMD-TOC-ANCHOR-2"></a>
### Folder organization <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The following structure for the `lua` folder is mandatory. Only the name `lua` can be chosen freely by the contributor: the name must be related to the technology used to produce new palettes.

~~~
+ lua
    + dev
    + fake-prod
    + palettes
    + readme
    + status
    + tests
    * extend.py
~~~
<a id="MULTIMD-TOC-ANCHOR-3"></a>
### The dev folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is the sole responsibility of the contributor. Its purpose is to provide a simple way to create and test new palettes.

<a id="MULTIMD-TOC-ANCHOR-4"></a>
### The tests folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

his directory should provide a way to test palette transformations.

<a id="MULTIMD-TOC-ANCHOR-5"></a>
### The palettes folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is used to store palettes provided as files using the specific implementation chosen. Each file name gives the name of the palette.
For example, on December 20, 2025, the `Lua` `palettes` folder contained the following items defining three palettes named `BlindFish`, `GasFlame`, and `GroovyRainbow`.

~~~
- palettes
    * BlindFish.lua
    * BurningGrass.lua
    * GasFlame.lua
    * GeoRainbow.lua
    * Lemon.lua
    * PastelRainbow.lua
    * ShiftRainbow.lua
~~~

In this folder, for example, we had the following `BlindFish.lua` file generated mainly by the `extend.py` file, which we will discuss soon.

~~~lua
------
-- this::
--     author = Christophe, Bal
--
--
-- Here is the luadraw code used.
--
-- lua::
--      _ , myFireBrick = mixcolor(FireBrick, .75, LightSalmon, .25)
--
--     PALETTE = {
--       Gray,
--       SlateGray,
--       LightSkyBlue,
--       LightPink,
--       Pink,
--       LightSalmon,
--       myFireBrick,
--     }
------

PALETTE = {
  {0.502, 0.502, 0.502},
  {0.4392, 0.502, 0.5647},
  {0.5294, 0.8078, 0.9804},
  {1, 0.7137, 0.7569},
  {1, 0.7529, 0.7961},
  {1, 0.6275, 0.4784},
  {0.7735, 0.25685, 0.219575}
}
~~~
> ***NOTE.*** *The size of palettes provided by `@prism` is fixed, but nothing prevents you from using any number of colors you wish when creating your own.*

<a id="MULTIMD-TOC-ANCHOR-6"></a>
### The status folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder allows you to know the status of your proposal. Its structure mimics the folder of contributions: `YAML` files correspond to contribution files. They indicate whether a contribution has been accepted or not, along with the reason for this status. ***No coding skill is needed to read these `YAML` files.***

<a id="MULTIMD-TOC-ANCHOR-7"></a>
### The extend.py file <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This file must follow the following commented template.

~~~python
#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

from typing import TypeAlias

import ast
import re


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = [float, float, float]
PaletteCols:TypeAlias = list[RGBCols]


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
def parse(code: str) -> PaletteCols:
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
#     Except if it is totally impossible, the code build must offer
#     the ability to access a palette via the string name of the
#     variable associated with it, and also to propose ways to
#     transform palettes (extraction, shift and reverse order).
###
def build_code(
    credits : str,
    palettes: dict[str, PaletteCols]
) -> str:
    ...


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    ...
~~~
<a id="MULTIMD-TOC-ANCHOR-8"></a>
### The fake-prod folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is a template used to create the final version of the implementation.
It must contain a palette file named as indicated in `extend.py` (the content of this mandatory file can be fake).

> ***NOTE.*** *A good practice is to provide a `showcase` folder for local testing without requiring installation.*

> ***CAUTION.*** *The `fake-prod` folder can't be used for palette creation.*

> ***WARNING.*** *Make sure to leave nothing unnecessary, as the structure will be copied entirely.*

<a id="MULTIMD-TOC-ANCHOR-9"></a>
### The readme folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `README.md` file of the contribution folder is written in small sections in the `readme` folder which has the following mandatory structure. These sections will also be used to produce documentations for the final product.

~~~
- readme
    * about.yaml
    * how-to-create.md
    * how-to-use.md
    * title.md
~~~

Here is the purpose of each of these files.

1. **`about.yaml` must not be changed.** It gives the way to gather the `MD` files to build the `README.md` file of the specific contribution folder.
2. `title.md` is the title for the specific technology. You can add here a short description.
3. `how-to-create.md` gives the process to follow to create new palettes as a developer.
4. `how-to-use.md` explains how to use one of the `@prism` palettes available as a user.

> ***WARNING.*** *`how-to-use.md` is used for building the `PDF` documentation with `LaTeX` in the background. Although this introduces some writing limitations, the validation process will guide you past them. For example, to achieve inline colored code, which `Markdown` doesn't support, do like in the following example. You can use as many magic comments `<!--YAML ... -->` as necessary, inserting them wherever you like.*

~~~markdown
<!--YAML
inlinecode:
  lua:
    - palGistHeat
    - getPal('GistHeat')
    - getPal('palGistHeat')
-->

The `Lua` palette names...

  * `palGistHeat` is a `Lua` variable.

  * `getPal('GistHeat')` and `getPal('palGistHeat')`...
~~~
