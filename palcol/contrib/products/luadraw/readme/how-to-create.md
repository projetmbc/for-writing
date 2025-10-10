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
% Test your palette here. Once you are satisfied with your work,
% copy and paste the file ''PROJECT-PALETTE.lua'' into the 
% ''contrib/palettes/luadraw/palettes'' folder, giving it a name
% in ''UpperCamelCase” format. This file only uses floats such
% as to obtain portable palette definitions.
%
% caution::
%     You can use any luadraw colors, but you can't change the
%     \var name ''PALETTE'' needed to automate some tasks.
%
% note::
%     In the Lua palette file, the ''author'' field is optional.
%%%

\begin{filecontents*}[overwrite]{__tmp-palette__.lua}
-- author: First Name, Last Name

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
