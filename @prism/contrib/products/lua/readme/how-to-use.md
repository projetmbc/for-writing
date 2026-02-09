Use a Lua palette
-----------------

#### Basic use

<!-- FORMAT SUPPORTED - AUTO - START -->
> ***NOTE.*** *All formats are provided: modular (each palette is in a dedicated file) and monolithic (files provide all the palettes).*
<!-- FORMAT SUPPORTED - AUTO - END -->


<!--YAML
inlinecode:
  lua:
    - palGistHeat
-->

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
palBlackbodyTransformed = palCreateFromPal(
    palBlackbody,
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
