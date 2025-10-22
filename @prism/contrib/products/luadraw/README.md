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

You can use palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.

> ***NOTE.*** *Initially, the `at-prism` project was created to provide ready-to-use palettes for `luadraw`.*

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
% copy and paste the file ''PROJECT-PALETTE.lua'' into the
% ''contrib/palettes/luadraw/palettes'' folder, giving it a name
% in ''UpperCamelCase” format. This file only uses floats such
% as to obtain portable palette definitions.
%
% caution::
%     You can use any luadraw colors, but you can't change the
%     variable name ''PALETTE'' needed to automate some tasks.
%
% note::
%     In the Lua palette file, the ''author'' field is optional.
%%%

\begin{filecontents*}[overwrite]{__tmp-palette__.lua}
------
-- this::
--     author = First Name, Last Name
------

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
