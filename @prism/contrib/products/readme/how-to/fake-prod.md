### The fake-prod folder

This folder is a template used to create the final version of the implementation.
It must contain fake, or real, palette and API files using the following standard names where `<ext>` is the extension of the technology implemented.

  * Palette files can be name `palettes-hf.<ext>`,  `palettes-hf/<palName>.<ext>`, `palettes-s40.<ext>` and `palettes-s40/<palName>.<ext>`.

  * `palapi.<ext>` represents the implementation of the API.


> ***NOTE.*** *A good practice is to provide a `showcase` folder for local testing without requiring installation. Try to propose simplified graphics like in the `Lua` product.*


> ***CAUTION.*** *The `fake-prod` folder can't be used for palette creation.*


> ***WARNING.*** *Make sure to leave nothing unnecessary, as the structure will be copied entirely.*
