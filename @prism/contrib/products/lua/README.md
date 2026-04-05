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
For instance, the following snippet is an excerpt from `palettes-hf/Accent.lua`.

~~~lua
palAccent = {
    {0.4980392157, 0.7882352941, 0.4980392157},
    {0.7450980392, 0.6823529412, 0.831372549},
    ...
}
~~~
#### Creating palettes from existing ones

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
Create a palette using Lua
--------------------------

For the moment, development requires working with `LaTeX` and the `luadraw` package: refer to the `TEX` files in the `dev/luadraw` folder.
