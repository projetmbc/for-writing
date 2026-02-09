Supported implementations
-------------------------

All implementations are located in the `products` folder. Each implementation provides the following features:

  * Palette formats in both modular (one file per palette) and monolithic (all palettes in a single file) versions.

  * Palette definitions in both high-fidelity (original size) and small (currently 40 colors) size.

  * Select specific colors from an existing palette using their indices.

  * Shift the palette left (negative value) or right (positive value) by any number of steps.

  * Reverse the order of the colors.


> ***IMPORTANT.*** *To explain how new palettes can be built, we will refer to the colors in the standard palette as `coul_1`, `coul_2`, etc., and suppose that the extracted indices are `{1, 3, 6, 9}`, the shift used is `+1`, and the `reverse` option is enabled. The new palette will then be built sequentially as follows: first `{coul_1, coul_3, coul_6, coul_9}` (extraction), second `{coul_9, coul_1, coul_3, coul_6}` (shift to the right), and finally `{coul_6, coul_3, coul_1, coul_9}` (reverse).*


> ***NOTE.*** *Extra features are limited to discrete palette operations. For example, color interpolation is not provided, as this is usually handled out of the box by visualization and formatting tools.*


### JSON, the versatile default format

The `JSON` product allows unsupported programming languages to integrate `@prism` palettes easily. Below are the first lines of the `palettes-hf.json` file.

<!-- JSON PALETTE FIRST LINES. AUTO - START -->
~~~json
{
  "Accent": [
    [0.49803922, 0.78823529, 0.49803922],
    [0.74509804, 0.68235294, 0.83137255],
    [0.99215686, 0.75294118, 0.5254902],
    [1, 1, 0.6],
    [0.21960784, 0.42352941, 0.69019608],
    [0.94117647, 0.00784314, 0.49803922],
    [0.74901961, 0.35686275, 0.09019608],
    [0.4, 0.4, 0.4]
  ],
  ...
}
~~~
<!-- JSON PALETTE FIRST LINES. AUTO - END -->
