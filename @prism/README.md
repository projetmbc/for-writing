<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


The @prism project
==================

**Table of contents**

<a id="MULTIMD-GO-BACK-TO-TOC"></a>
- [About @prism](#MULTIMD-TOC-ANCHOR-0)
- [Credits](#MULTIMD-TOC-ANCHOR-1)
- [Supported implementations](#MULTIMD-TOC-ANCHOR-2)
    - [JSON, the versatile default format](#MULTIMD-TOC-ANCHOR-3)
    - [luadraw palettes](#MULTIMD-TOC-ANCHOR-4)
        - [Description](#MULTIMD-TOC-ANCHOR-5)
        - [Use a luadraw palette](#MULTIMD-TOC-ANCHOR-6)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
About @prism <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
------------

This project provides a collection of discrete color palettes for various programming languages,
enabling the creation and use of color maps derived from these palettes.

> ***CAUTION.*** *Only discrete palettes are provided. No continuous colormaps are implemented.*

<a id="MULTIMD-TOC-ANCHOR-1"></a>
Credits <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------

`@prism` includes some original creations, but most color palettes are derived from the project below by segmenting their color maps into 10-value palettes.

- [`Asymptote`](https:asymptote.sourceforge.io) is used, but currently offers nothing beyond [`Matplotlib`](https://matplotlib.org) (despite different implementa- tions).
- [`Colorbrewer`](https://colorbrewer2.org).
- [`Cubehelix`](https://jiffyclub.github.io/palettable/cubehelix) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Matplotlib`](https://matplotlib.org).
- [`Scientific Coulour Maps`](https://www.fabiocrameri.ch/colourmaps).
- [`Tableau`](https://www.tableau.com) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Wes Anderson Palettes`](https://wesandersonpalettes.tumblr.com) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.

> ***IMPORTANT.*** *`@prism` only uses `CamelCase` names with no characters other than numbers and ASCII letters. For example, a name such as `nipy_spectral-1` is transformed into `NipySpectral1` within `@prism`.*

<a id="MULTIMD-TOC-ANCHOR-2"></a>
Supported implementations <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------------

The implementations are inside the folder `products`.

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### JSON, the versatile default format <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

By default, a file `palettes.json` is provided to allow unsupported coding languages to also integrate `@prism` palettes. Here are the first line of this file.

~~~json
{
  "Accent": [
    [0.498039, 0.788235, 0.498039],
    [0.690196, 0.705881, 0.757298],
    [0.882352, 0.721568, 0.661437],
    [0.99477, 0.835294, 0.550326],
    [0.913289, 0.935947, 0.610021],
    [0.306317, 0.487581, 0.680174],
    [0.700653, 0.146404, 0.562091],
    [0.855772, 0.162962, 0.316775],
    [0.671459, 0.366448, 0.159041],
    [0.4, 0.4, 0.4]
  ],
  ...
}
~~~
<a id="MULTIMD-TOC-ANCHOR-4"></a>
### luadraw palettes <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

<a id="MULTIMD-TOC-ANCHOR-5"></a>
#### Description <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

You can use `@prism` palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use palettes for `luadraw`.*

<a id="MULTIMD-TOC-ANCHOR-6"></a>
#### Use a luadraw palette <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by three ways.

- `palGistHeat` is a `Lua` variable.
- `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.
- `palNames['palGistHeat']` is equal to `palGistHeat`.

> ***NOTE.*** *The `Lua` palette variables are arrays of arrays of three floats. Here is the definition of `palGistHeat`.*

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.105882, 0.0, 0.0},
    {0.211764, 0.0, 0.0},
    {0.317647, 0.0, 0.0},
    {0.429411, 0.0, 0.0},
    {0.535294, 0.0, 0.0},
    {0.641176, 0.0, 0.0},
    {0.752941, 0.003921, 0.0},
    {0.858823, 0.145098, 0.0},
    {0.964705, 0.286274, 0.0},
    {1.0, 0.42745, 0.0},
    {1.0, 0.57647, 0.152941},
    {1.0, 0.717647, 0.435294},
    {1.0, 0.858823, 0.717647},
    {1.0, 1.0, 1.0}
}
~~~

The `getPal` function has some options. To explain how this works, let's consider the following use case.

~~~lua
mypal = getPal(
    'GistHeat',
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~

To simplify the explanations, we will refer to the colors
in the standard palette `'GistHeat'` as `coul_1`, `coul_2`, etc. The options are then **processed in the following order**.

1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.
2. `{coul_9, coul_2, coul_5, coul_8}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).
3. `{coul_8, coul_5, coul_2, coul_9}` is the reversed version of the shifted palette.

> ***NOTE.*** *The reversed version of any palette can be obtained using `getPal(palname, {reverse = true})`.*
