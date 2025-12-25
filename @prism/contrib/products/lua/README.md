<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


Lua
===

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use color palettes for [`luadraw`](https://github.com/pfradin/luadraw), a package that greatly facilitates the creation of high-quality 2D and 3D plots using `LuaLaTeX` and `TikZ`. The `Lua` implementation is now integrated into [`luadraw`](https://github.com/pfradin/luadraw).*

Use a Lua palette
-----------------

#### Simple use

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
#### Creating palettes from existing ones

The `getPal` function provides several options to easily build new palettes by transforming existing ones. To illustrate how this works, consider the following use case.

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

To simplify the explanations, we will refer to the colors in the standard palette `'GistHeat'` as `coul_1`, `coul_2`, etc. The options are then **processed in the following order**.

1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.
2. `{coul_9, coul_2, coul_5, coul_8}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).
3. `{coul_8, coul_5, coul_2, coul_9}` is the reversed version of the shifted extracted palette.

Create a palette using Lua
--------------------------

For the moment, development requires working with `LaTeX` and the `luadraw` package: refer to the `TEX` files in the `dev/luadraw` folder.
