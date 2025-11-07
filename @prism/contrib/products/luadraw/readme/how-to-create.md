<!--YAML
inlinecode:
  lua:
    - PALETTE
-->

Create a palette using luadraw
------------------------------

Palettes are created using `luadraw` via the file `dev/main.tex`, which produces illustrative examples of use.

~~~
- dev
    + core
    * main.tex
~~~


The design is done by modifying the `PALETTE` variable at the beginning of the file `dev/main.tex`. See below.

~~~latex
% !TEX TS-program = lualatex

%%%
% This file allows you to test a palette directly: when compiling
% the document, a ''PROJECT-PALETTE.lua'' file is automatically
% created. Once satisfied with the result, simply copy and paste
% the ''PROJECT-PALETTE.lua'' file into the folder
% ''contrib/palettes/luadraw/palettes'', giving it a name in
% ''CamelCase'' format (this file uses only floating-point numbers
% to ensure portable palette definitions).
%
%
% caution::
%     You can use any luadraw colors, but you can't change the
%     variable name ''PALETTE'' needed to automate some tasks.
%
%
% note::
%     In the Lua palette file, the ''author'' field is optional.
%%%

\begin{filecontents*}[overwrite]{__tmp-palette__.lua}
------
-- this::
--     author = First Name, Last Name
------

PALETTE = {
  Gray,
  SlateGray,
  LightSkyBlue,
  LightPink,
  Pink,
  LightSalmon,
  FireBrick,
}
\end{filecontents*}

% ...
~~~
