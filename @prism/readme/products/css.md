<!-------------------------------------------
  -- AUTOMATICALLY GENERATED - DO NOT EDIT --
  ------------------------------------------->


### CSS

> ***NOTE.*** *The `HTML`, `CSS`, and `JavaScript` files for product development and demonstration were created using `Claude` and `Gemini` AI assistants.*


<!-- FORMAT SUPPORTED - AUTO - START -->
> ***NOTE.*** *All formats are provided: modular (each palette is in a dedicated file) and monolithic (files provide all the palettes).*
<!-- FORMAT SUPPORTED - AUTO - END -->


<!--YAML
inlinecode:
  css:
    - --pal<name>-<nb>
    - <name>
    - <nb>
-->

Each palette color is defined as an individual variable named according to the pattern `--pal<name>-<nb>`, where `<name>` is the standard palette name and `<nb>` is the desired index ranging.
Each palette color variable is defined as an `RGB` value using percentage notation.
For example, the file `palettes-hf/GistHeat.css` looks like the following partial code.

~~~css
:root {
  --palGistHeat-1: rgb(0% 0% 0%);
  --palGistHeat-2: rgb(0.59% 0% 0%);
  /* Other RBG colors.*/
  --palGistHeat-255: rgb(100% 99.22% 98.43%);
  --palGistHeat-256: rgb(100% 100% 100%);
}
~~~


Here is one first possible use case.

~~~css
.warning-text {
  color: var(--palGistHeat-3);
}

.gist-heat-gradient {
  background: linear-gradient(
    90deg,
    var(--palGistHeat-1),
    var(--palGistHeat-64),
    var(--palGistHeat-128),
    var(--palGistHeat-256)
  );
}
~~~


The example below demonstrates creating gradient variables through selective color extraction and custom reordering.

~~~css
:root {
  --transformed-gist-heat-gradient: linear-gradient(
    90deg,
    var(--palGistHeat-6),
    var(--palGistHeat-3),
    var(--palGistHeat-9),
    var(--palGistHeat-1)
  );
}

.transformed-gist-heat-gradient {
  background: var(--transformed-gist-heat-gradient);
}
~~~
