<!-------------------------------------------
  -- AUTOMATICALLY GENERATED - DO NOT EDIT --
  ------------------------------------------->


### CSS

> ***NOTE.*** *The `HTML`, `CSS`, and `JavaScript` files for product development and demonstration were created using `Claude` and `Gemini` AI assistants.*


<!--YAML
inlinecode:
  css:
    - --pal<name>-<nb>
    - <name>
    - <nb>
-->

Each palette color is defined as an individual variable named according to the pattern `--pal<name>-<nb>`, where `<name>` is the standard palette name and `<nb>` is the desired index ranging.
Each palette color variable is defined as an `RGB` value using percentage notation.
For example, the file `palettes-hf/Accent.css` looks like the following partial code.

<!-- CSS PALETTE FIRST LINES. AUTO - START -->
~~~css
:root {
  --palAccent-1: rgb(49.803922% 78.823529% 49.803922%);
  --palAccent-2: rgb(74.509804% 68.235294% 83.137255%);
  --palAccent-3: rgb(99.215686% 75.294118% 52.54902%);
  ...
}
~~~
<!-- CSS PALETTE FIRST LINES. AUTO - END -->


The following example illustrates how to generate gradient variables via selective color extraction and custom reordering, while using a standalone color for warning text.

~~~css
:root {
  --transformed-accent-gradient: linear-gradient(
    90deg,
    var(--palAccent-6),
    var(--palAccent-3),
    var(--palAccent-8),
    var(--palAccent-1)
  );
}

.transformed-accent-gradient {
  background: var(--transformed-accent-gradient);
}

.warning-text {
  color: var(--palAccent-3);
}
~~~
