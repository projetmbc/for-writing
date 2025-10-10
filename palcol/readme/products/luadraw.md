### luadraw palettes

#### Description

You can use palettes with [`luadraw`][1] which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLatex` and `TikZ`.


> ***NOTE.*** *Initially, the `palcol` project was created to provide ready-to-use palettes for `luadraw`.*


[1]: https://github.com/pfradin/luadraw


#### Use a luadraw palette

The names of the palettes all use the prefix `pal` followed by the name available in the file `palcol.json`. These variables are arrays of arrays of three floats. Here is the definition of one randomly selected palettes.

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
