### lua palettes
> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use palettes for [`luadraw`][1] which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLaTeX` and `TikZ`.*


[1]: https://github.com/pfradin/luadraw


#### Use a lua palette

<!--YAML
inlinecode:
  lua:
    - palGistHeat
    - getPal
    - getPal('GistHeat')
    - getPal('palGistHeat')
    - palNames['palGistHeat']
    - getPal(palname, {reverse = true})
-->

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by three ways.

  * `palGistHeat` is a `Lua` variable.

  * `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.

  * `palNames['palGistHeat']` is equal to `palGistHeat`.


> ***NOTE.*** *The `Lua` palette variables are arrays of arrays of three floats. The definition of `palGistHeat` looks like the following partial code.*

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.105882, 0.0, 0.0},
    {0.211764, 0.0, 0.0},
    -- ... With 7 more RBG colors.
}
~~~


<!--YAML
inlinecode:
  lua:
    - 'GistHeat'
    - coul_1
    - coul_2
    - mypal = {coul_2, coul_5, coul_8, coul_9}
    - mypal = {coul_5, coul_8, coul_9, coul_2}
    - mypal = {coul_2, coul_9, coul_8, coul_5}
-->

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

  1. `{coul_9, coul_2, coul_5, coul_8}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).

  1. `{coul_8, coul_5, coul_2, coul_9}` is the reversed version of the shifted palette.

> ***NOTE.*** *The reversed version of any palette can be obtained using `getPal(palname, {reverse = true})`.*
