<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


LaTeX
=====

Use a LaTeX palette
-------------------

#### Basic use

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
#### Creating palettes from scratch

For creating new palettes manually, the following high-level commands are available.

1. `\palCreateFromNames` works with a comma separated list of named colors, while `\palCreateFromRGB` creates a palette by entering it as an array-like variable of arrays of three floats.
2. `\palSize{<name>}` returns the palette size (useful for loops, for example).

The following example demonstrates the `\palCreateFromRGB` and `\palCreateFromNames` commands.

~~~latex
\usepackage{palapi}
\usepackage[svgnames]{xcolor}

\palCreateFromRGB{MyRGBPal}{
  {0.0, 0.0, 0.0},
  {0.8, 0.2, 0.0},
}

\palCreateFromNames{MyNameUsePal}{
  YellowGreen,
  green!60!black,
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
#### Creating palettes from existing ones

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

#### Retrieving the internal definition of a palette

The internally stored definition of a palette named `MyPal`, for example, is `\g_palette_MyPal_seq` which is a `L3` variable (keep in mind the pattern `\g_palette_PaletteName_seq`).

> ***NOTE.*** *Variables of type `\g_palette_PaletteName_seq` are not used internally to retrieve the colors themselves; they are only there for technical reasons related to the development process of new palettes via `LaTeX`.*

Create a palette using LaTeX
----------------------------

The development involves working with `LaTeX` and `TikZ`: refer to the `TEX` files in the `dev` folder.
