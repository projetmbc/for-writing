<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


CSS
===

> ***NOTE.*** *The `HTML`, `CSS`, and `JavaScript` files for product development and demonstration were created using `Claude` and `Gemini` AI assistants.*

Use a CSS palette
-----------------

Each palette color is defined as an individual variable named according to the pattern `--pal<name>-<nb>`, where `<name>` is the standard palette name and `<nb>` is the desired index ranging.
Each palette color variable is defined as an `RGB` value using percentage notation.
For example, the file `palettes-hf/Accent.css` looks like the following partial code.

~~~css
:root {
  --palAccent-1: rgb(49.803922% 78.823529% 49.803922%);
  --palAccent-2: rgb(74.509804% 68.235294% 83.137255%);
  --palAccent-3: rgb(99.215686% 75.294118% 52.54902%);
  /* Other RBG colors.*/
}
~~~

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
Create a palette using CSS
--------------------------

Development workflow uses the `dev/test-dark-or-std.html` `HTML` file, which features an intuitive interface.
When you're satisfied with your palette, save the downloaded file to the `contrib/palettes/css/palettes` folder.

> ***NOTE.*** *This approach provides an efficient method for rapid palette iteration and prototyping.*
