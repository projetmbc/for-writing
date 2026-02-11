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
    - [The about.yaml file](#MULTIMD-TOC-ANCHOR-7)
    - [The extend.py file](#MULTIMD-TOC-ANCHOR-8)
    - [The fake-prod folder](#MULTIMD-TOC-ANCHOR-9)
    - [The readme folder](#MULTIMD-TOC-ANCHOR-10)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
Structure of the contrib/products folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
----------------------------------------

We will briefly explain the following structure of the `contrib/products` folder.

~~~
+ products
  + changes
  + contributils
  + readme
  + status
  + template-stucture
  + [...]
~~~

Here is how the different folders are used.

1. `changes` is used to communicate changes related to contributions.
2. `contributils` is a small module for easily implementing the `extend.py` `Python` file for contributions.
3. `readme`, managed by the `@prism` developer, is used to generate the `contrib/products/README.md` file.
4. `status`, managed by the `@prism` developer, contains `YAML` files indicating whether an implementation has been accepted or not, along with the reason for this status. ***No coding skill is needed to read these `YAML` files.***
5. `template-structure` provides a starting structure for adding new implementations.
6. The other folders are the contributions themselves, the development process for which is explained in the following section.

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
  * about.yaml
  * extend.py
  + dev
  + fake-prod
  + palettes
  + readme
  + status
  + tests
~~~
<a id="MULTIMD-TOC-ANCHOR-3"></a>
### The dev folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is the sole responsibility of the contributor. Its purpose is to provide a simple way to create and test new palettes.

<a id="MULTIMD-TOC-ANCHOR-4"></a>
### The tests folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This directory shoulds provide a way to test palette transformations.

> ***NOTE.*** This is a good place to retrieve the API. You can then copy the content of the API file when building the final product (this trick is used by the `Lua` product).

<a id="MULTIMD-TOC-ANCHOR-5"></a>
### The palettes folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is used to store palettes provided as files using the specific implementation chosen. Each file name gives the name of the palette.
For example, on December 20, 2025, the `Lua` `palettes` folder contained the following items defining palettes named `BlindFish`, `BurningGrass`, `GasFlame`...

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

In this folder, for example, we have the following `BlindFish.lua` file generated mainly by the `extend.py` file, which we will discuss soon.

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
<a id="MULTIMD-TOC-ANCHOR-6"></a>
### The status folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder allows you to know the status of your proposal. Its structure mimics the folder of contributions: `YAML` files correspond to contribution files. They indicate whether a contribution has been accepted or not, along with the reason for this status. ***No coding skill is needed to read these `YAML` files.***

<a id="MULTIMD-TOC-ANCHOR-7"></a>
### The about.yaml file <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This file defines the cleanup tasks for production deployment and the output formats to be generated. All available keys are listed below, followed by their detailed usage.

~~~yaml
modular   : ...
monolithic: ...
clean     :
  data  : ...
  gobble: ...
~~~

By default, all formats are generated. If a technology cannot produce a specific format, use `monolithic: no` to omit all-in-one files, and `modular: no` to skip individualized files.

To clean up the contribution folder, the `gobble` sub-key allows to provide a list of gobble patterns using paths relative to the contribution root.
To simplify maintenance, the `data` sub-key adds the possibility to define virtual variables as lists of sub-patterns.
For instance, in the following dummy example, using `dev/luadraw/*.latex_temp_ext` is equivalent to specifying `dev/luadraw/*.aux` and `dev/luadraw/*.log`.

~~~yaml
clean:
  data:
    latex_temp_ext:
      - aux
      - log

  gobble:
    - dev/luadraw/*.\latex_temp_ext
~~~
<a id="MULTIMD-TOC-ANCHOR-8"></a>
### The extend.py file <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This file must follow the following template. The comments help you get started with coding. Take also a look at the existing products.

~~~python
#!/usr/bin/env python3

###
# To simplify coding, the small ''contributils'' module
# imported below provides the ''PaletteTransformer'' class,
# which streamlines feature engineering.
###

# --------------------------------- #
# -- IMPORT CONTRIBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR          = Path(__file__).parent
CONTRIB_PRODS_DIR = THIS_DIR.parent

sys.path.append(str(CONTRIB_PRODS_DIR))

from contributils import *

# -- IMPORT CONTRIBUTILS - END -- #
# ------------------------------- #


# --------------------------------- #
# -- SINGLE PALETTE CODE BUILDER -- #
# --------------------------------- #

###
# prototype::
#     name    : name of one single palette.
#     palette : one single palette.
#
#     :return: the code of ''palette'' for the final product
#              versions.
#
#
# warning::
#     All tecnhologies must implement a ''_build_palette''
#     function.
###
def _build_palette(
    name   : str,
    palette: PaletteCols
) -> str:
    ...


# ---------------------- #
# -- API CODE BUILDER -- #
# ---------------------- #

###
# prototype::
#     :return: the code of the \api of the final product.
#
#
# warning::
#     Except if it is totally impossible, the code build must
#     offer the ability to access a palette via the string name
#     of the variable associated with it, and also to propose
#     ways totransform palettes (extraction, shift and reverse
#     order). Therefore, the lines below should be removed if
#     the technology does not provide an API.
###
def _build_api() -> str:
    ...


# ------------------------- #
# -- PALETTE TRANSFORMER -- #
# ------------------------- #

###
# The ''PaletteTransformer'' class requires four mandatory
# arguments and offers five optional parameters.
#
#     1) ''extension'' is the extension of the files to build.
#
#     1) ''comspecs'' is a dictionnary to specify multiline
#     and/or single comments.
#
#     1) ''palpattern'' is a regex to extract colors from a
#     palette defined in a specific technology.
#
#     1) ''pal_builder'' is a function that builds the code of
#     a single palette.
#
#     1) ''api_builder'' is a function that builds the API code
#     (if there is one).
#
#     1) ''floatify'' is used to make a flot from one string color
#     extracted.
#
#     1) ''header'' can be used to add some specific lines before
#     the palette codes.
#
#     1) ''footer'' can be used to add some specific lines after
#     the palette codes.
#
#     1) ''titledeco'' is the single character used to frame the
#     titles in special comments.
###
paltransfo = PaletteTransformer(
    extension   = ...,
    comspecs    = ...,
    palpattern  = ...,
    pal_builder = ...,
    api_builder = ...,  # OPTIONAL.
    floatify    = ...,  # OPTIONAL.
    titledeco   = ...,  # OPTIONAL.
    header      = ...,  # OPTIONAL.
    footer      = ...,  # OPTIONAL.
)


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    ...
~~~
<a id="MULTIMD-TOC-ANCHOR-9"></a>
### The fake-prod folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

This folder is a template used to create the final version of the implementation.
It must contain fake, or real, palette and API files using the following standard names where `<ext>` is the extension of the technology implemented.

- Palette files can be name `palettes-hf.<ext>`, `palettes-hf/<palName>.<ext>`, `palettes-s40.<ext>` and `palettes-s40/<palName>.<ext>`.
- `palapi.<ext>` represents the implementation of the API.

> ***NOTE.*** *A good practice is to provide a `showcase` folder for local testing without requiring installation. Try to propose simplified graphics like in the `Lua` product.*

> ***CAUTION.*** *The `fake-prod` folder can't be used for palette creation.*

> ***WARNING.*** *Make sure to leave nothing unnecessary, as the structure will be copied entirely.*

<a id="MULTIMD-TOC-ANCHOR-10"></a>
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

> ***WARNING.*** *`how-to-use.md` is used for building the `PDF` documentation with `LaTeX` in the background. Although this introduces some writing limitations, the validation process will guide you past them. For example, to achieve inline colored code, which `Markdown` doesn't support, do like in the following example. You can use as many magic comments `<!--YAML ... -->` as necessary, inserting them wherever you want.*

~~~markdown
<!--YAML
inlinecode:
  lua:
    - palGistHeat
-->

... the definition of `palGistHeat` looks like ...
~~~
