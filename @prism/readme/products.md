Supported implementations
-------------------------

All implementations are located in the `products` folder. Each implementation provides palette definitions and supports the use of a single color. When available, the following actions can be performed to create new palettes:

  * Select specific colors from an existing palette.

  * Shift the palette left or right by any number of steps.

  * Reverse the order of the colors.


> ***NOTE.*** *Extra features are limited to discrete palette operations. For example, color interpolation is not provided, as this is usually handled out of the box by visualization and formatting tools.*


### JSON, the versatile default format

A `palettes.json` file containing only palette definitions is provided by default, allowing unsupported programming languages to integrate `@prism` palettes. Below are the first lines of the file.

<!-- JSON PALETTE FIRST LINES. AUTO - START -->
~~~json
{
  "Accent": [
    [0.498039, 0.788235, 0.498039],
    [0.690196, 0.705881, 0.757298],
    [0.882352, 0.721568, 0.661437],
    [0.99477, 0.835294, 0.550326],
    [0.913289, 0.935947, 0.610021],
    [0.306317, 0.487581, 0.680174],
    [0.700653, 0.146404, 0.562091],
    [0.855772, 0.162962, 0.316775],
    [0.671459, 0.366448, 0.159041],
    [0.4, 0.4, 0.4]
  ],
  ...
}
~~~
<!-- JSON PALETTE FIRST LINES. AUTO - END -->
