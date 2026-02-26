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
    - [CSS](#MULTIMD-TOC-ANCHOR-4)
    - [LaTeX](#MULTIMD-TOC-ANCHOR-5)
        - [Basic use](#MULTIMD-TOC-ANCHOR-6)
        - [Creating palettes from scratch](#MULTIMD-TOC-ANCHOR-7)
        - [Creating palettes from existing ones](#MULTIMD-TOC-ANCHOR-8)
        - [Retrieving the internal definition of a palette](#MULTIMD-TOC-ANCHOR-9)
    - [Lua](#MULTIMD-TOC-ANCHOR-10)
        - [Basic use](#MULTIMD-TOC-ANCHOR-11)
        - [Creating palettes from existing ones](#MULTIMD-TOC-ANCHOR-12)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
About @prism <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
------------

This project provides a collection of discrete color palettes for various programming languages,
enabling the creation and use of color maps derived from these palettes.

> ***NOTE.*** *For a simple live demonstration, [click here](https://projetmbc.github.io/for-writing/@prism/showcase/dark-or-std-mode.html).*

> ***CAUTION.*** *Only discrete palettes are provided. No continuous colormaps are implemented.*

<a id="MULTIMD-TOC-ANCHOR-1"></a>
Credits <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------

`@prism` includes some original creations, but most color palettes are derived from the project below by segmenting their color maps into 10-value palettes.

- [`Asymptote`](https:asymptote.sourceforge.io) is used, but currently offers nothing beyond [`Matplotlib`](https://matplotlib.org) (despite different implementa- tions).
- [`CarbonPlan`](https://github.com/carbonplan/colormaps) provides palettes designed for data visualization.
- [`CartoColor`](https://github.com/CartoDB/cartocolor) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`cmocean`](https://matplotlib.org/cmocean) is extracted from [`Palettable`](https://github.com/jiffyclub/palettable) project.
- [`Colorbrewer`](https://colorbrewer2.org).
- [`Colormaps`](https://github.com/pratiman-91/colormaps).
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

All implementations are located in the `products` folder. Each implementation provides the following features.

- Modular palette formats (one file per palette).
- Palette definitions in both high-fidelity (original size) and small (currently 40 colors) size.

Most implementations also feature the API explained below.

- Select specific colors from an existing palette using their indices.
- Shift the palette left (negative value) or right (positive value) by any number of steps.
- Reverse the order of the colors.

> ***IMPORTANT.*** *To explain how new palettes can be built, we will refer to the colors in the standard palette as `coul_1`, `coul_2`, etc., and suppose that the extracted indices are `{1, 3, 6, 9}`, the shift used is `+1`, and the `reverse` option is enabled. The new palette will then be built sequentially as follows: first `{coul_1, coul_3, coul_6, coul_9}` (extraction), second `{coul_9, coul_1, coul_3, coul_6}` (shift to the right), and finally `{coul_6, coul_3, coul_1, coul_9}` (reverse).*

> ***NOTE.*** *Extra features are limited to discrete palette operations. For example, color interpolation is not provided, as this is usually handled out of the box by visualization and formatting tools.*

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### JSON, the versatile default format <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `JSON` product enables seamless `@prism` palette integration for unsupported programming languages. As shown below, palettes are defined using nested arrays of three-component floats.

~~~json
[
  [0.4980392157, 0.7882352941, 0.4980392157],
  [0.7450980392, 0.6823529412, 0.831372549],
  [0.9921568627, 0.7529411765, 0.5254901961],
  ...
]
~~~
<a id="MULTIMD-TOC-ANCHOR-4"></a>
### CSS <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

> ***NOTE.*** *The `HTML`, `CSS`, and `JavaScript` files for product development and demonstration were created using `Claude` and `Gemini` AI assistants.*

Each palette color is defined as an individual variable named according to the pattern `--pal<name>-<nb>`, where `<name>` is the standard palette name and `<nb>` is the desired index ranging.
Each palette color variable is defined as an `RGB` value using percentage notation.
For example, the file `palettes-hf/Accent.css` looks like the following partial code.

~~~css
:root {
  --palAccent-1: rgb(49.803922% 78.823529% 49.803922%);
  --palAccent-2: rgb(74.509804% 68.235294% 83.137255%);
  --palAccent-3: rgb(99.215686% 75.294118% 52.54902%);
  /* Other RBG colors.*/
}
~~~

The following example illustrates how to generate gradient variables via selective color extraction and custom reordering, while using a standalone color for warning text.

~~~css
:root {
  --transformed-accent-gradient: linear-gradient(
    90deg,
    var(--palAccent-6),
    var(--palAccent-3),
    var(--palAccent-8),
    var(--palAccent-1)
  );
}

.transformed-accent-gradient {
  background: var(--transformed-accent-gradient);
}

.warning-text {
  color: var(--palAccent-3);
}
~~~
<a id="MULTIMD-TOC-ANCHOR-5"></a>
### LaTeX <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

<a id="MULTIMD-TOC-ANCHOR-6"></a>
#### Basic use <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

Accessing a single palette color is straightforward: use `\palUse{<name>}{<index>}` where `<name>` is the standard palette name (without prefix), and `<index>` is the color number.
For example, `\palUse{Accent}{8}` is the eighth color of the `Accent` palette, an `xcolor` format color that can be easily used as shown in the following compilable example.

~~~latex
\documentclass{article}

% Load the wanted palette.
\usepackage{palettes-hf/Accent}

% Load the palette API.
\usepackage{palapi}

\usepackage{tikz}

\begin{document}

\textcolor{\palUse{Accent}{8}}{\bfseries Colored text.}

Representation of the first ten palette colors.

\begin{tikzpicture}
  \foreach \i in {1,...,10} {
    \fill[\palUse{Accent}{\i}]
      (1.25*\i - 1, 0) rectangle (1.25*\i, 1);
  }
\end{tikzpicture}

\end{document}
~~~
<a id="MULTIMD-TOC-ANCHOR-7"></a>
#### Creating palettes from scratch <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

For creating new palettes manually, the following high-level commands are available.

1. `\palCreateFromNames` works with a comma separated list of named colors, while `\palCreateFromRGB` creates a palette by entering it as an array-like variable of arrays of three floats.
2. `\palSize{<name>}` returns the palette size (useful for loops, for example).

The following example demonstrates the `\palCreateFromRGB` and `\palCreateFromNames` commands.

~~~latex
\usepackage{palapi}

\usepackage[svgnames]{xcolor}

\palCreateFromRGB{MyRGBPal}{
  {0.0, 0.0, 0.0},
  {0.4, 0.0, 0.2},
  {0.8, 0.2, 0.0},
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
\usepackage{palapi}

\usepackage[svgnames]{xcolor}

\palNew{LowLevelPal}
\palAddNames{LowLevelPal}{IndianRed}
\palAddRGB{LowLevelPal}{0.0, 0.0, 0.0}
\palAddNames{LowLevelPal}{green!60!black}
\palAddRGB{LowLevelPal}{0.8, 0.2, 0.0}
~~~
<a id="MULTIMD-TOC-ANCHOR-8"></a>
#### Creating palettes from existing ones <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

Building new palettes by transforming existing ones can be achieved using the `\palCreateFromPal` command, which has the signature `\palCreateFromPal{<new-name>}[<options>]{<existing-name>}`.
The following example shows how to do this (all options are used).

~~~latex
\usepackage{palettes-hf/Accent}
\usepackage{palapi}

\palCreateFromPal{AccentTransformed}[
  extract = {1, 3, 6, 9},
  shift   = 1,
  reverse
]{Accent}
~~~
> ***TIP.*** *`\palCreateFromPal{<new-name>}{<existing-name>}` builds a copy of an existing palette.*

<a id="MULTIMD-TOC-ANCHOR-9"></a>
#### Retrieving the internal definition of a palette <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The internally stored definition of a palette named `MyPal`, for example, is `\g_palette_MyPal_seq` which is a `L3` variable (keep in mind the pattern `\g_palette_PaletteName_seq`).

> ***NOTE.*** *Variables of type `\g_palette_PaletteName_seq` are not used internally to retrieve the colors themselves; they are only there for technical reasons related to the development process of new palettes via `LaTeX`.*

<a id="MULTIMD-TOC-ANCHOR-10"></a>
### Lua <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use color palettes for [`luadraw`](https://github.com/pfradin/luadraw), a package that greatly facilitates the creation of high-quality 2D and 3D plots using `LuaLaTeX` and `TikZ`.*

<a id="MULTIMD-TOC-ANCHOR-11"></a>
#### Basic use <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `Lua` palette variables are named using the prefix `pal`.
They are arrays of arrays of three floats (making it straightforward to use a color from a palette).
For example, the file `palettes-hf/Accent.lua` looks like the following partial code.

~~~lua
palAccent = {
    {0.4980392157, 0.7882352941, 0.4980392157},
    {0.7450980392, 0.6823529412, 0.831372549},
    {0.9921568627, 0.7529411765, 0.5254901961},
    -- Other RBG colors.
}
~~~
<a id="MULTIMD-TOC-ANCHOR-12"></a>
#### Creating palettes from existing ones <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `palCreateFromPal` function provides options to build new palettes by transforming existing ones.
The following example shows how to do this (all options are used).

~~~lua
palAccentTransformed = palCreateFromPal(
    palAccent,
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
