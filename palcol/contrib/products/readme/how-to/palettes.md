### The 'palettes' folder

This folder is used to store palettes provided as files using the specific implementation chosen. Each file name gives the name of the palette.
For example, on October 14, 2025, the `palettes` folder contained the following items defining three palettes named `BlindFish`, `GasFlame`, and `GroovyRainbow`.

~~~
- palettes
    * BlindFish.lua
    * BurningGrass.lua
    * GasFlame.lua
    * GeoRainbow.lua
    * PastelRainbow.lua
~~~


In this folder, for example, we had the following `BlindFish.lua` file generated mainly by the `extend.py` file, which we will discuss soon.

~~~lua
-- author: Christophe, Bal

-- ludraw definition used.

-- PALETTE = {
--   Gray,
--   SlateGray,
--   LightSkyBlue,
--   LightPink,
--   Pink,
--   LightSalmon,
--   FireBrick,
-- }

PALETTE = {
  {0.502, 0.502, 0.502},
  {0.4392, 0.502, 0.5647},
  {0.5294, 0.8078, 0.9804},
  {1, 0.7137, 0.7569},
  {1, 0.7529, 0.7961},
  {1, 0.6275, 0.4784},
  {0.698, 0.1333, 0.1333}
}
~~~
