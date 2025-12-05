<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


lua palettes
============

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use palettes for [`luadraw`](https://github.com/pfradin/luadraw) which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.*

Create a palette using lua
--------------------------

> ***CAUTION.*** *Only the folders `dev` (for creation) and `palettes` (for submission) are used for palette creation. Don't modify any other folders.*

For the moment, development requires working with `LaTeX` and the `luadraw` package: refer to the `TEX` files in the `dev/luadraw` folder.

Use a lua palette
-----------------

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by three ways.

- `palGistHeat` is a `Lua` variable.
- `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.
- `palNames['palGistHeat']` is equal to `palGistHeat`.

> ***NOTE.*** *The `Lua` palette variables are arrays of arrays of three floats. The definition of `palGistHeat` looks like the following partial code.*

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.105882, 0.0, 0.0},
    {0.211764, 0.0, 0.0},
    -- ... With 7 more RBG colors.
}
~~~

The `getPal` function has some options. To explain how this works, let's consider the following use case.

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
in the standard palette `'GistHeat'` as `coul_1`, `coul_2`, etc. The options are then **processed in the following order**.

1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.
2. `{coul_9, coul_2, coul_5, coul_8}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).
3. `{coul_8, coul_5, coul_2, coul_9}` is the reversed version of the shifted palette.

> ***NOTE.*** *The reversed version of any palette can be obtained using `getPal(palname, {reverse = true})`.*
