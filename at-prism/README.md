<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


The at-prism project
====================

**Table of contents**

<a id="MULTIMD-GO-BACK-TO-TOC"></a>
- [About at-prism](#MULTIMD-TOC-ANCHOR-0)
- [Credits](#MULTIMD-TOC-ANCHOR-1)
- [Supported implementations](#MULTIMD-TOC-ANCHOR-2)
    - [JSON, the versatile default format](#MULTIMD-TOC-ANCHOR-3)
    - [luadraw palettes](#MULTIMD-TOC-ANCHOR-4)
        - [Description](#MULTIMD-TOC-ANCHOR-5)
        - [Use a luadraw palette](#MULTIMD-TOC-ANCHOR-6)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
About at-prism <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
--------------

This project provides a collection of discrete color palettes for various programming languages,
enabling the creation and use of color maps derived from these palettes.

> ***CAUTION.*** *Only discrete palettes are provided. No continuous colormaps are implemented.*

<a id="MULTIMD-TOC-ANCHOR-1"></a>
Credits <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------

Many of the discrete color palettes in this project are based on colormaps from [`Asymptote`](https://asymptote.sourceforge.io/) and [`Matplotlib`](https://matplotlib.org/).
If you recognize your contribution, please don’t hesitate to get in touch, we’ll be happy to give you proper credit in the source code.

> ***IMPORTANT.*** *`at-prism` only uses camel case names with no characters other than numbers and ASCII letters. For example, a name such as `nipy_spectral-1` is transformed into `NipySpectral1` within `at-prism`.*

<a id="MULTIMD-TOC-ANCHOR-2"></a>
Supported implementations <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------------

The implementations are inside the folder `products`.

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### JSON, the versatile default format <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

By default, a file `products/palettes.json` is provided to allow unsupported coding languages to easily integrate palettes. Here are the first line of this file.

~~~json
{
  "Accent": [
    [0.498039, 0.788235, 0.498039],
    [0.621568, 0.735293, 0.664705],
    [0.745098, 0.682352, 0.831372],
    [0.868627, 0.717646, 0.678431],
    [0.992156, 0.752941, 0.52549],
    [0.996078, 0.87647, 0.562744],
    [1.0, 1.0, 0.6],
    [0.609803, 0.711764, 0.645098],
    [0.219607, 0.423529, 0.690196],
    [0.580391, 0.215686, 0.594117],
    [0.941176, 0.007842, 0.498039],
    [0.845097, 0.182352, 0.294117],
    [0.749019, 0.356862, 0.090196],
    [0.574509, 0.378431, 0.245097],
    [0.4, 0.4, 0.4]
  ],
  "Afmhot": [
    [0.0, 0.0, 0.0],
    [0.141176, 0.0, 0.0],
    [0.282352, 0.0, 0.0],
    [0.423529, 0.0, 0.0],
    [0.572549, 0.072549, 0.0],
    [0.713725, 0.213725, 0.0],
    [0.854901, 0.354901, 0.0],
    [1.0, 0.50392, 0.003921],
    [1.0, 0.645098, 0.145098],
    [1.0, 0.786274, 0.286274],
    [1.0, 0.92745, 0.42745],
    [1.0, 1.0, 0.57647],
    [1.0, 1.0, 0.717647],
    [1.0, 1.0, 0.858823],
    [1.0, 1.0, 1.0]
  ],
  ...
}
~~~
<a id="MULTIMD-TOC-ANCHOR-4"></a>
### luadraw palettes <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

<a id="MULTIMD-TOC-ANCHOR-5"></a>
#### Description <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

You can use palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.

> ***NOTE.*** *Initially, the `at-prism` project was created to provide ready-to-use palettes for `luadraw`.*

<a id="MULTIMD-TOC-ANCHOR-6"></a>
#### Use a luadraw palette <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The palette names all use the prefix `pal` followed by the name available in the file `at-prism.json`. You can acces a palette by two ways.

- `palGistHeat` is a palette variable.
- `getPal("GistHeat")` and `getPal("palGistHeat")` are equal to `palGistHeat`.

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
