<!-------------------------------------------
  -- AUTOMATICALLY GENERATED - DO NOT EDIT --
  ------------------------------------------->


### Lua

> ***NOTE.*** *Initially, the `@prism` project was created to provide ready-to-use color palettes for [`luadraw`][1], a package that greatly facilitates the creation of high-quality 2D and 3D plots using `LuaLaTeX` and `TikZ`.*


[1]: https://github.com/pfradin/luadraw


#### Basic use

<!--YAML
inlinecode:
  lua:
    - pal
-->

The `Lua` palette variables are named using the prefix `pal`.
They are arrays of arrays of three floats (making it straightforward to use a color from a palette).
For example, the file `palettes-hf/Accent.lua` looks like the following partial code.

<!-- LUA PALETTE SAMPLE -  AUTO - START -->
~~~lua
palAccent = {
    {0.4980392157, 0.7882352941, 0.4980392157},
    {0.7450980392, 0.6823529412, 0.831372549},
    {0.9921568627, 0.7529411765, 0.5254901961},
    ...
}
~~~
<!-- LUA PALETTE FIRST LINES. AUTO - END -->


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
palAccentTransformed = palCreateFromPal(
    palAccent,
    {
        extract = {2, 5, 8, 9},
        shift   = 1,
        reverse = true
    }
)
~~~
