### Tools

Sometimes, external files are needed, as is the case with the parser `contrib/parser/code/licence.py`. Here's how to work with external files.

  1. Each file must be used in the same folder as the `Python` file.

  1. The file name must be prefixed by the parser name followed by an hyphen like with the additional file `license-spdx.json` for the `Python` file `license.py`.

  1. The files must be added, or build via functions placed in the `TOOLS` section, which will import the necessary modules (see the last section, "Magic Comments", for additional explanations).


---


> ***NOTE.*** *Working with files stored permanently on the end user's operating system is a good practice to adopt for obvious security reasons, but also for offline use.*
