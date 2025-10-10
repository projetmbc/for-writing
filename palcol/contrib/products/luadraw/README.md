<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


luadraw palettes
================

Description
-----------

You can use palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLatex` and `TikZ`.

> ***NOTE.*** *Initially, the `palcol` project was created to provide ready-to-use palettes for `luadraw`.*

Create a palette using luadraw
------------------------------

Palettes are created using `luadraw` via the file `dev/main.tex`, which produces illustrative examples of use.

~~~
- dev
    + core
    * main.tex
~~~

The design is done by modifying the `PALETTE` variable at the beginning of the file `dev/main.tex`. See below.

~~~latex
% !TEX TS-program = lualatex

%%%
% Test your palette here. Once you are satisfied with your work,
% copy and paste the file ''PROJECT-PALETTE.luadraw.lua'' into
% the ''contrib/palettes/luadraw/final'' folder, giving it a name
% in ''UpperCamelCase” format. This file only uses floats in order
% to make the palette definition portable.
%
% caution::
%     Keep the extended extension ''luadraw.lua''.
%%%

%%%
% warning::
%     You can use any luadraw colors, but you can't change the
%     \var name ''PALETTE''.
%
% note::
%     The ''author'' field is optional.
%%%

\begin{filecontents*}[overwrite]{__tmp-palette__.lua}
-- author: First Name, Last Name

PALETTE = {
  Gray,
  SlateGray,
  LightSkyBlue,
  LightPink,
  Pink,
  LightSalmon,
  FireBrick,
}
\end{filecontents*}

% ...
~~~
Use a luadraw palette
---------------------

The names of the palettes all use the prefix `pal` followed by the name available in the file `palcol.json`. These variables are arrays of arrays of three floats. Here is the definition of one randomly selected palettes.

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
