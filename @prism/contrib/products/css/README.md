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

The very basic `CSS` implementation provides only ten variables per palette, named according to the pattern `--pal<name>-<nb>`, where `<name>` is the standard palette name and `<nb>` is the desired index ranging from 1 to 10.
Each palette color variable is defined as an `RGB` value using percentage notation.
For example, the `GistHeat` palette color definitions look like the following partial code.

~~~css
:root {
  /* Previous palettes. */

  --palGistHeat-1 = rgb(0% 0% 0.0%)
  --palGistHeat-2 = rgb(10.5882% 0% 0%)
  --palGistHeat-3 = rgb(21.1764% 0% 0%)
  /* ... With 7 more RBG colors.*/

  /* Additional palettes. */
}
~~~

Here are two possible use cases.

~~~css
.warning-text {
  color: var(--palGistHeat-3);
}

.gist-heat-gradient {
  background: linear-gradient(
    90deg,
    var(--palGistHeat-1),
    var(--palGistHeat-2),
    var(--palGistHeat-3),
    var(--palGistHeat-4),
    var(--palGistHeat-5),
    var(--palGistHeat-6),
    var(--palGistHeat-7),
    var(--palGistHeat-8),
    var(--palGistHeat-9),
    var(--palGistHeat-10)
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
Create a palette using CSS
--------------------------

Development workflow uses the `dev/test-dark-or-std.html` `HTML` file, which features an intuitive interface.
When you're satisfied with your palette, save the downloaded file to the `contrib/palettes/css/palettes` folder.

> ***NOTE.*** *This approach provides an efficient method for rapid palette iteration and prototyping.*
