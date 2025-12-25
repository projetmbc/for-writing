### LaTeX


#### Simple use

<!--YAML
inlinecode:
  latex:
    - \palUse{<name>}{<indice>}
    - \palUse{GistHeat}{3}
-->

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


#### Creating palettes manually

<!--YAML
inlinecode:
  latex:
    - \palSize{<name>}
    - \palCreateFromRGB
    - \palCreateFromName
-->

For creating new palettes manually, the following high-level commands are available.

  1. `\palSize{<name>}` returns the palette size (useful for loops, for example).

  1. `\palCreateFromRGB` creates a palette by entering it as a `Lua` array, while `\palCreateFromName` works with named colors.

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

\palCreateFromName{MyNamedPal}{
  YellowGreen,
  LimeGreen,
  green!60!black,
}

\begin{document}

\foreach \name in {MyRGBPal, MyNamedPal}{
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

<!--YAML
inlinecode:
  latex:
    - \palNew{<name>}
    - \palAddName{<name>}{<color-names>}
    - \palAddRGB{<name>}{<r>, <g>, <b>}
-->

A lower-level approach is also available through the following commands.

  1. `\palNew{<name>}` defines a new (empty) palette.

  1. `\palAddName{<name>}{<color-names>}` appends a color using named colors to the palette.

  1. `\palAddRGB{<name>}{<r>, <g>, <b>}` appends an `RGB` color to the palette, where `<r>`, `<g>`, and `<b>` are decimal values ranging from 0 to 1.

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

TODO
