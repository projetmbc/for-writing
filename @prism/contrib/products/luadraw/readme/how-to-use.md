Use a luadraw palette
---------------------

<!--YAML
inlinecode:
  lua:
    - palGistHeat
    - getPal("GistHeat")
    - getPal("palGistHeat")
-->

The palette names all use the prefix `pal` followed by the name available in the file `@prism.json`. You can acces a palette by two ways.

  * `palGistHeat` is a palette variable.

  * `getPal("GistHeat")` and `getPal("palGistHeat")` are equal to `palGistHeat`.


> ***NOTE.*** *The palette variables are arrays of arrays of three floats. Here is the definition of the palette `palGistHeat`.*

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
    - "GistHeat"
    - coul_1
    - coul_2
    - mypal = {coul_2, coul_5, coul_8, coul_9}
    - mypal = {coul_5, coul_8, coul_9, coul_2}
    - mypal = {coul_2, coul_9, coul_8, coul_5}
-->

There are also some options. To explain how this works, let's consider the following use case.

~~~lua
mypal = getPal(
    "GistHeat",
    {
        extract = {2, 5, 8, 9},
        shift   = 3,
        reverse = true
    }
)
~~~

To simplify the explanations, we will refer to the colors
in the standard palette `"GistHeat"` as `coul_1`, `coul_2,`, etc. The options are then processed in the following order.

  1. `{coul_2, coul_5, coul_8, coul_9}` is the result of the extraction.

  1. `{coul_5, coul_8, coul_9, coul_2}` comes from the shifting applied to the extracted palette (colors move to the right if `shift` is positive).

  1. `{coul_2, coul_9, coul_8, coul_5}` is the reversed version of the previous palette.
