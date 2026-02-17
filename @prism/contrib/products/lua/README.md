<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


Lua
===

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use color palettes for [`luadraw`](https://github.com/pfradin/luadraw), a package that greatly facilitates the creation of high-quality 2D and 3D plots using `LuaLaTeX` and `TikZ`.*

Use a Lua palette
-----------------

#### Basic use

The `Lua` palette variables are named using the prefix `pal`.
They are arrays of arrays of three floats (making it straightforward to use a color from a palette).
For example, the definition of `palGistHeat` looks like the following partial code.

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.105882, 0.0, 0.0},
    {0.211764, 0.0, 0.0},
    -- Other RBG colors.
}
~~~
#### Creating palettes from existing ones

The `palCreateFromPal` function provides options to build new palettes by transforming existing ones.
The following example shows how to do this (all options are used).

~~~lua
palBlackbodyTransformed = palCreateFromPal(
    palBlackbody,
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
Create a palette using Lua
--------------------------

For the moment, development requires working with `LaTeX` and the `luadraw` package: refer to the `TEX` files in the `dev/luadraw` folder.
