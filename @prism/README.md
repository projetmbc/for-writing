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

Many of the discrete color palettes in this project are based on colormaps from [`Asymptote`](https://asymptote.sourceforge.io/) and [`Matplotlib`](https://matplotlib.org/).
If you recognize your contribution, please don’t hesitate to get in touch, we’ll be happy to give you proper credit in the source code.

> ***IMPORTANT.*** *`@prism` only uses camel case names with no characters other than numbers and ASCII letters. For example, a name such as `nipy_spectral-1` is transformed into `NipySpectral1` within `@prism`.*

<a id="MULTIMD-TOC-ANCHOR-2"></a>
Supported implementations <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------------

The implementations are inside the folder `products`.

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### JSON, the versatile default format <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

By default, a file `palettes.json` is provided to allow unsupported coding languages to easily integrate palettes. Here are the first line of this file.

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
  "Acton": [
    [0.1494, 0.049588, 0.2492],
    [0.211157, 0.137645, 0.329252],
    [0.267471, 0.218184, 0.402887],
    [0.320544, 0.293914, 0.471806],
    [0.384817, 0.36079, 0.532262],
    [0.470163, 0.386092, 0.553794],
    [0.558642, 0.393025, 0.558478],
    [0.65637, 0.400265, 0.563305],
    [0.759601, 0.420022, 0.578967],
    [0.823456, 0.494153, 0.641178],
    [0.852947, 0.587004, 0.720314],
    [0.879746, 0.680664, 0.798213],
    [0.902848, 0.769828, 0.867187],
    [0.922771, 0.849827, 0.927307],
    [0.93986, 0.91915, 0.97935]
  ],
  ...
}
~~~
<a id="MULTIMD-TOC-ANCHOR-4"></a>
### luadraw palettes <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

<a id="MULTIMD-TOC-ANCHOR-5"></a>
#### Description <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

You can use palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use palettes for `luadraw`.*

<a id="MULTIMD-TOC-ANCHOR-6"></a>
#### Use a luadraw palette <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The palette names all use the prefix `pal` followed by the name available in the file `@prism.json`. You can acces a palette by two ways.

- `palGistHeat` is a palette variable.
- `getPal("GistHeat")` and `getPal("palGistHeat")` are equal to `palGistHeat`.

> ***NOTE.*** *The palette variables are arrays of arrays of three floats. Here is the definition of the palette `palGistHeat`.*

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

There are also some options. To explain how this works, let's consider the following use case.

~~~lua
mypal = getPal(
    "GistHeat",
    {
        extract = {2, 5, 8, 9},
        shift   = 3,
        reverse = true
    }
)
~~~

To simplify the explanations, we will refer to the colors
in the standard palette `"GistHeat"` as `coul_1`, `coul_2,`, etc. The options are then processed in the following order.

1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.
2. `{coul_5, coul_8, coul_9, coul_2}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).
3. `{coul_2, coul_9, coul_8, coul_5}` is the reversed version of the previous palette.
