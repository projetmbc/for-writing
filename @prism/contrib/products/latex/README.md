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

#### Simple use

To use a color from a palette, use `\palUse{<name>}{<index>}` where `<name>` is the standard palette name (without prefix), and `<index>` is the color number (ranging from 1 to 10).
For example, `\palUse{GistHeat}{8}` is the eighth color of the `GistHeat` palette, an `xcolor` format color that can be easily used as shown in the following example.

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
#### Creating palettes from scratch

For creating new palettes manually, the following high-level commands are available.

1. `\palCreateFromRGB` creates a palette by entering it as a `Lua` array, while `\palCreateFromName` works with named colors.
2. `\palSize{<name>}` returns the palette size (useful for loops, for example).

The following example demonstrates these commands.

~~~latex
\documentclass{article}

\usepackage{palettes}
\usepackage[dvipsnames, svgnames]{xcolor}
\usepackage{tikz}

\palCreateFromRGB{MyRGBPal}{
  {0.0, 0.0, 0.0},
  {0.4, 0.0, 0.2},
  {0.8, 0.2, 0.0},
  {1.0, 0.6, 0.0},
  {1.0, 1.0, 0.4},
}

\palCreateFromName{MyNameUsePal}{
  YellowGreen,
  LimeGreen,
  green!60!black,
}

\begin{document}

\foreach \name in {MyRGBPal, MyNameUsePal}{
  \section*{\name}

  \textcolor{\palUse{\name}{3}}{\bfseries Colored text.}

  \bigskip

  \begin{tikzpicture}
    \foreach \i in {1,...,\palSize{\name}} {
      \fill[\palUse{\name}{\i}]
        (1.25*\i - 1, 0) rectangle (1.25*\i, 1);
    }
  \end{tikzpicture}
}

\end{document}
~~~

A lower-level approach is also available through the following commands.

1. `\palNew{<name>}` defines a new (empty) palette.
2. `\palAddName{<name>}{<color-using-names>}` appends a color defined with named colors to the palette.
3. `\palAddRGB{<name>}{<r>, <g>, <b>}` appends an `RGB` color to the palette, where `<r>`, `<g>`, and `<b>` are decimal values ranging from 0 to 1.

The following example demonstrates the flexibility offered by these low-level commands.

~~~latex
\documentclass{article}

\usepackage{palettes}
\usepackage[svgnames]{xcolor}
\usepackage{tikz}

\palNew{LowLevelPal}
\palAddName{LowLevelPal}{IndianRed}
\palAddRGB{LowLevelPal}{0.0, 0.0, 0.0}
\palAddName{LowLevelPal}{green!60!black}
\palAddRGB{LowLevelPal}{0.8, 0.2, 0.0}

\begin{document}

\begin{tikzpicture}
  \foreach \i in {1,...,\palSize{LowLevelPal}} {
     \fill[\palUse{LowLevelPal}{\i}]
      (1.25*\i - 1, 0) rectangle (1.25*\i, 1);
  }
\end{tikzpicture}

\end{document}
~~~
#### Creating palettes from existing ones

Building new palettes by transforming existing ones can be achieved using the `\palCreateFromPal` command, which has the signature `\palCreateFromPal{<new-name>}[<options>]{<existing-name>}`. To illustrate how this works, consider the following use case.

~~~latex
\documentclass{article}

\usepackage{palettes}
\usepackage{tikz}

\palCreateFromPal{BlackbodyTransformed}[
  extract = {1, 3, 6, 9},
  shift   = 1,
  reverse
]{Blackbody}

\begin{document}

Original color palette.

\begin{tikzpicture}
  \foreach \i in {1,...,10} {
    \fill[\palUse{Blackbody}{\i}]
      (1.25*\i - 1, 0) rectangle (1.25*\i, 1);
  }
\end{tikzpicture}

New color palette.

\begin{tikzpicture}
  \foreach \i in {1,...,4} {
    \fill[\palUse{BlackbodyTransformed}{\i}]
      (1.25*\i - 1, 0) rectangle (1.25*\i, 1);
  }
\end{tikzpicture}

\end{document}
~~~

To simplify the explanations, we will refer to the colors in the standard palette `'Blackbody'` as `coul_1`, `coul_2`, etc. The options are then **processed in the following order**.

1. `{coul_1, coul_3, coul_6, coul_9}` is the result of the extraction.
2. `{coul_9, coul_1, coul_3, coul_6}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).
3. `{coul_6, coul_3, coul_1, coul_9}` is the reversed version of the shifted extracted palette.

Create a palette using LaTeX
----------------------------

TODO
