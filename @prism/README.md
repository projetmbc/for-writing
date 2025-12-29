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
    - [LaTeX](#MULTIMD-TOC-ANCHOR-4)
        - [Basic use](#MULTIMD-TOC-ANCHOR-5)
        - [Creating palettes from scratch](#MULTIMD-TOC-ANCHOR-6)
        - [Creating palettes from existing ones](#MULTIMD-TOC-ANCHOR-7)
        - [Retrieving the internal definition of a palette](#MULTIMD-TOC-ANCHOR-8)
    - [Lua](#MULTIMD-TOC-ANCHOR-9)
        - [Basic use](#MULTIMD-TOC-ANCHOR-10)
        - [Creating palettes from existing ones](#MULTIMD-TOC-ANCHOR-11)

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
- [`CartoColor`](https://github.com/CartoDB/cartocolor) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`cmocean`](https://matplotlib.org/cmocean) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Colorbrewer`](https://colorbrewer2.org).
- [`Cubehelix`](https://jiffyclub.github.io/palettable/cubehelix) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Light and Bartlein`](https://jiffyclub.github.io/palettable/lightbartlein) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Matplotlib`](https://matplotlib.org).
- [`MyCarta`](https://mycartablog.com/color-palettes) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Plotly`](https://plotly.com/python) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Scientific Coulour Maps`](https://www.fabiocrameri.ch/colourmaps).
- [`Tableau`](https://www.tableau.com) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Wes Anderson Palettes`](https://wesandersonpalettes.tumblr.com) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.

> ***IMPORTANT.*** *`@prism` only uses `CamelCase` names with no characters other than numbers and ASCII letters. For example, a name such as `nipy_spectral-1` is transformed into `NipySpectral1` within `@prism`.*

<a id="MULTIMD-TOC-ANCHOR-2"></a>
Supported implementations <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------------

All implementations are located in the `products` folder. Each implementation provides palette definitions and supports the use of a single color. When available, the following actions can be performed to create new palettes:

- Select specific colors from an existing palette using their indices.
- Shift the palette left (negative value) or right (positive value) by any number of steps.
- Reverse the order of the colors.

> ***IMPORTANT.*** *To explain how new palettes can be built, we will refer to the colors in the standard palette as `coul_1`, `coul_2`, etc., and suppose that the extracted indices are `{1, 3, 6, 9}`, the shift used is `+1`, and the `reverse` option is enabled. The new palette will then be built sequentially as follows: first `{coul_1, coul_3, coul_6, coul_9}` (extraction), second `{coul_9, coul_1, coul_3, coul_6}` (shift to the right), and finally `{coul_6, coul_3, coul_1, coul_9}` (reverse).*

> ***NOTE.*** *Extra features are limited to discrete palette operations. For example, color interpolation is not provided, as this is usually handled out of the box by visualization and formatting tools.*

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### JSON, the versatile default format <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

A `palettes.json` file containing only palette definitions is provided by default, allowing unsupported programming languages to integrate `@prism` palettes. Below are the first lines of the file.

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
### LaTeX <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

<a id="MULTIMD-TOC-ANCHOR-5"></a>
#### Basic use <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

To use a color from a palette, use `\palUse{<name>}{<index>}` where `<name>` is the standard palette name (without prefix), and `<index>` is the color number (ranging from 1 to 10).
For example, `\palUse{GistHeat}{8}` is the eighth color of the `GistHeat` palette, an `xcolor` format color that can be easily used as shown in the following compilable example.

~~~latex
\documentclass{article}

\usepackage{palettes}
\usepackage{tikz}

\begin{document}

\textcolor{\palUse{GistHeat}{8}}{\bfseries Colored text.}

Representation of the color palette.

\begin{tikzpicture}
  \foreach \i in {1,...,10} {
    \fill[\palUse{GistHeat}{\i}]
      (1.25*\i - 1, 0) rectangle (1.25*\i, 1);
  }
\end{tikzpicture}

\end{document}
~~~
<a id="MULTIMD-TOC-ANCHOR-6"></a>
#### Creating palettes from scratch <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

For creating new palettes manually, the following high-level commands are available.

1. `\palCreateFromRGB` creates a palette by entering it as an array-like variable, while `\palCreateFromNames` works with named colors.
2. `\palSize{<name>}` returns the palette size (useful for loops, for example).

The following example demonstrates the `\palCreateFromRGB` and `\palCreateFromNames` commands (we don't have put `\usepackage{palettes}`).

~~~latex
\usepackage[svgnames]{xcolor}

\palCreateFromRGB{MyRGBPal}{
  {0.0, 0.0, 0.0},
  {0.4, 0.0, 0.2},
  {0.8, 0.2, 0.0},
  {1.0, 0.6, 0.0},
  {1.0, 1.0, 0.4},
}

\palCreateFromNames{MyNameUsePal}{
  YellowGreen,
  green!60!black,
  LimeGreen!80,
}
~~~
> ***NOTE.*** *All built-in palettes are created using the `\palCreateFromRGB` macro.*

A lower-level approach is also available through the following commands.

1. `\palNew{<name>}` initializes a new (empty) palette.
2. `\palAddNames{<name>}{<color-using-names>}` appends a color defined with named colors to the palette.
3. `\palAddRGB{<name>}{<r>, <g>, <b>}` appends an `RGB` color to the palette, where `<r>`, `<g>`, and `<b>` are decimal values ranging from 0 to 1.

The following example demonstrates the flexibility offered by these low-level commands.

~~~latex
\usepackage[svgnames]{xcolor}

\palNew{LowLevelPal}
\palAddNames{LowLevelPal}{IndianRed}
\palAddRGB{LowLevelPal}{0.0, 0.0, 0.0}
\palAddNames{LowLevelPal}{green!60!black}
\palAddRGB{LowLevelPal}{0.8, 0.2, 0.0}
~~~
<a id="MULTIMD-TOC-ANCHOR-7"></a>
#### Creating palettes from existing ones <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

Building new palettes by transforming existing ones can be achieved using the `\palCreateFromPal` command, which has the signature `\palCreateFromPal{<new-name>}[<options>]{<existing-name>}`.
The following example shows how to do this (all options are used).

~~~latex
\palCreateFromPal{BlackbodyTransformed}[
  extract = {1, 3, 6, 9},
  shift   = 1,
  reverse
]{Blackbody}
~~~
> ***TIP.*** *`\palCreateFromPal{<new-name>}{<existing-name>}` build a copy of an existing palette.*

<a id="MULTIMD-TOC-ANCHOR-8"></a>
#### Retrieving the internal definition of a palette <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The internally stored definition of a palette named `MyPal`, for example, is `\g_palette_MyPal_seq` which is a `L3` variable (keep in mind the pattern `\g_palette_PaletteName_seq`).

> ***NOTE.*** *Variables of type `\g_palette_PaletteName_seq` are not used internally to retrieve the colors themselves; they are only there for technical reasons related to the development process of new palettes via `LaTeX`.*

<a id="MULTIMD-TOC-ANCHOR-9"></a>
### Lua <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use color palettes for [`luadraw`](https://github.com/pfradin/luadraw), a package that greatly facilitates the creation of high-quality 2D and 3D plots using `LuaLaTeX` and `TikZ`. The `Lua` implementation is now integrated into [`luadraw`](https://github.com/pfradin/luadraw).*

<a id="MULTIMD-TOC-ANCHOR-10"></a>
#### Basic use <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by two ways.

- `palGistHeat` is a `Lua` variable.
- `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.

The `Lua` palette variables are arrays of ten arrays of three floats (making it straightforward to use a color from a palette).
For example, the definition of `palGistHeat` looks like the following partial code.

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.105882, 0.0, 0.0},
    {0.211764, 0.0, 0.0},
    -- ... With 7 more RBG colors.
}
~~~
<a id="MULTIMD-TOC-ANCHOR-11"></a>
#### Creating palettes from existing ones <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `getPal` function provides options to build new palettes by transforming existing ones.
The following example shows how to do this (all options are used).

~~~lua
BlackbodyTransformed = getPal(
    'Blackbody',
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
