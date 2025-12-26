### Lua

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use color palettes for [`luadraw`][1], a package that greatly facilitates the creation of high-quality 2D and 3D plots using `LuaLaTeX` and `TikZ`. The `Lua` implementation is now integrated into [`luadraw`][1].*


[1]: https://github.com/pfradin/luadraw


#### Basic use

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

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by two ways.

  * `palGistHeat` is a `Lua` variable.

  * `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.


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


<!-------------------->


#### Creating palettes from existing ones

The `getPal` function provides options to build new palettes by transforming existing ones.
The following example shows how to do this (all options are used).

~~~lua
BlackbodyTransformed = getPal(
    'Blackbody',
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
