Use a Lua palette
-----------------

#### Basic use

<!--YAML
inlinecode:
  lua:
    - palGistHeat
-->

The `Lua` palette names all use the prefix `pal` followed by the name available in the file `palettes.json`.
The `Lua` palette variables are arrays of ten arrays of three floats (making it straightforward to use a color from a palette).
For example, the definition of `palGistHeat` looks like the following partial code.

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.105882, 0.0, 0.0},
    {0.211764, 0.0, 0.0},
    -- Other RBG colors.
}
~~~


<!-------------------->


#### Creating palettes from existing ones

<!--YAML
inlinecode:
  lua:
    - palCreateFromPal
-->

The `palCreateFromPal` function provides options to build new palettes by transforming existing ones.
The following example shows how to do this (all options are used).

~~~lua
BlackbodyTransformed = palCreateFromPal(
    'Blackbody',
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
