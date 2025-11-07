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

You can use `@prism` palettes with [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use palettes for `luadraw`.*

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

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by two ways.

- `palGistHeat` is a `Lua` variable.
- `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.

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

There are also some options. To explain how this works, let's consider the following use case.

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
in the standard palette `'GistHeat'` as `coul_1`, `coul_2,`, etc. The options are then **processed in the following order**.

1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.
2. `{coul_9, coul_2, coul_5, coul_8}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).
3. `{coul_8, coul_5, coul_2, coul_9}` is the reversed version of the shifted palette.
