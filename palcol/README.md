<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


The palcol project
==================

**Table of contents**

<a id="MULTIMD-GO-BACK-TO-TOC"></a>
- [About palcol](#MULTIMD-TOC-ANCHOR-0)
- [Credits](#MULTIMD-TOC-ANCHOR-1)
- [Supported implementations](#MULTIMD-TOC-ANCHOR-2)
    - [JSON, the versatile default format](#MULTIMD-TOC-ANCHOR-3)
    - [luadraw palettes](#MULTIMD-TOC-ANCHOR-4)
        - [Description](#MULTIMD-TOC-ANCHOR-5)
        - [Use a luadraw palette](#MULTIMD-TOC-ANCHOR-6)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
About palcol <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
------------

This project provides a collection of discrete color palettes for various programming languages,
enabling the creation and use of color maps derived from these palettes.

> ***CAUTION.*** *Only discrete palettes are provided. No continuous colormaps are implemented.*

<a id="MULTIMD-TOC-ANCHOR-1"></a>
Credits <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------

Many of the discrete color palettes in this project are based on colormaps from [`Asymptote`](https://asymptote.sourceforge.io/) and [`Matplotlib`](https://matplotlib.org/).
If you recognize your contribution, please don’t hesitate to get in touch, we’ll be happy to give you proper credit in the source code.

> ***IMPORTANT.*** *`colpal` only uses camel case names with no characters other than numbers and ASCII letters. For example, a name such as `nipy_spectral-1` is tranformed into `NipySpectral1` within `palcol`.*

<a id="MULTIMD-TOC-ANCHOR-2"></a>
Supported implementations <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------------

The implementations are inside the folder `products`.

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### JSON, the versatile default format <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

By default, a file `products/palettes.json` is provided to allow unsupported coding languages to easily integrate palettes.

<a id="MULTIMD-TOC-ANCHOR-4"></a>
### luadraw palettes <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

<a id="MULTIMD-TOC-ANCHOR-5"></a>
#### Description <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

You can use palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLatex` and `TikZ`.

> ***NOTE.*** *Initially, the `palcol` project was created to provide ready-to-use palettes for `luadraw`.*

<a id="MULTIMD-TOC-ANCHOR-6"></a>
#### Use a luadraw palette <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The palette names all use the prefix `pal` followed by the name available in the file `palcol.json`. You can acces a palette by two ways.

- `palGistHeat` is a palette variable.
- `getPal[‘palGistHeat’]` is equal to `palGistHeat`.

> ***NOTE.*** *The palette variables are arrays of arrays of three floats. Here is the definition of the palette `palGistHeat`.*

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.21176, 0.0, 0.0},
    {0.42941, 0.0, 0.0},
    {0.64117, 0.0, 0.0},
    {0.85882, 0.14509, 0.0},
    {1.0, 0.42745, 0.0},
    {1.0, 0.71764, 0.43529},
    {1.0, 1.0, 1.0}
}
~~~
