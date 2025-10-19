Use a luadraw palette
---------------------

The palette names all use the prefix `pal` followed by the name available in the file `at-prism.json`. You can acces a palette by two ways.

  * `palGistHeat` is a palette variable.

  * `getPal("GistHeat")` and `getPal("palGistHeat")` are equal to `palGistHeat`.


> ***NOTE.*** *The palette variables are arrays of arrays of three floats. Here is the definition of the palette `palGistHeat`.*

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
