### The palettes folder

This folder is used to store palettes provided as files using the specific implementation chosen. Each file name gives the name of the palette.
For example, on December 20, 2025, the `Lua` `palettes` folder contained the following items defining palettes named `BlindFish`, `BurningGrass`, `GasFlame`...

~~~
- palettes
    * BlindFish.lua
    * BurningGrass.lua
    * GasFlame.lua
    * GeoRainbow.lua
    * Lemon.lua
    * PastelRainbow.lua
    * ShiftRainbow.lua
~~~


In this folder, for example, we have the following `BlindFish.lua` file generated mainly by the `extend.py` file, which we will discuss soon.

~~~lua
------
-- this::
--     author = Christophe, Bal
--
--
-- Here is the luadraw code used.
--
-- lua::
--      _ , myFireBrick = mixcolor(FireBrick, .75, LightSalmon, .25)
--
--     PALETTE = {
--       Gray,
--       SlateGray,
--       LightSkyBlue,
--       LightPink,
--       Pink,
--       LightSalmon,
--       myFireBrick,
--     }
------

PALETTE = {
  {0.502, 0.502, 0.502},
  {0.4392, 0.502, 0.5647},
  {0.5294, 0.8078, 0.9804},
  {1, 0.7137, 0.7569},
  {1, 0.7529, 0.7961},
  {1, 0.6275, 0.4784},
  {0.7735, 0.25685, 0.219575}
}
~~~
