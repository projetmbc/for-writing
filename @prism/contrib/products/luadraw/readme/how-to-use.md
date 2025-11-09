Use a luadraw palette
---------------------

<!--YAML
inlinecode:
  lua:
    - palGistHeat
    - getPal
    - getPal('GistHeat')
    - getPal('palGistHeat')
    - palNames
    - getPal(palname, {reverse = true})
-->

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`. You can access a palette by two ways.

  * `palGistHeat` is a `Lua` variable.

  * `getPal('GistHeat')` and `getPal('palGistHeat')` are equal to `palGistHeat`.

  * For compatibility reasons with the `luadraw` API, there is also an associative array called `palNames`, which expects the variable name with `pal` prefix. See the caution note at the end of this section.


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
in the standard palette `'GistHeat'` as `coul_1`, `coul_2,`, etc. The options are then **processed in the following order**.

  1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.

  1. `{coul_9, coul_2, coul_5, coul_8}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).

  1. `{coul_8, coul_5, coul_2, coul_9}` is the reversed version of the shifted palette.


> ***CAUTION.*** *The current version of `luadraw` simply uses the palettes provided by `@prism` wihtout the `getPal` function. If you prefer to use the `@prism` version with its `getPal` function, you will need to include the entire code in the `luadraw_palettes.lua` file where the package is installed.*


> ***NOTE.*** *The reversed version of any palette can be obtained using `getPal(palname, {reverse = true})`.*
