<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


Development tools
=================

The `tools` folder contains `Python` tools that are useful for developing the project, but are not part of the project itself.

**Table of contents**

<a id="MULTIMD-GO-BACK-TO-TOC"></a>
- [Initial structure of the tools folder](#MULTIMD-TOC-ANCHOR-0)
- [The launch.bash file](#MULTIMD-TOC-ANCHOR-1)
- [Turnkey tools](#MULTIMD-TOC-ANCHOR-2)
    - [Updating README.md files via multimd](#MULTIMD-TOC-ANCHOR-3)
    - [Contribution file documentation](#MULTIMD-TOC-ANCHOR-4)
- [Some basic utilities](#MULTIMD-TOC-ANCHOR-5)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
Initial structure of the tools folder <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------------------------

Here is the initial content of the `tools` folder proposed by cb-py-dev copier templates avaiable in [this page](https://github.com/projetmbc/copier-templates/tree/main/cb-py-dev), which serves as the basis for developing "in-house" tools.

~~~
+ tools
  + 01-contrib
    * 90-README-folders-struct.py
  + cbutils
    + core
  * launch.bash
  * 90-update-READMEs.py
  * README.md
~~~

The following sections explain how this set of files and folders works.

<a id="MULTIMD-TOC-ANCHOR-1"></a>
The launch.bash file <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
--------------------

The `launch.bash` file is used to launch all the tools. It works as follows.

1. The files to be launched are all `Python` files. They are sorted naturally using the `sort` command applied to their path relative to the `tools` folder. **This allows for sequential processing.**
2. The `tools/cbutils` folder is excluded from the search; it is the only one.
3. The `-q` option, or `--quick`, is used to ignore files whose names end with `-slow`.

<a id="MULTIMD-TOC-ANCHOR-2"></a>
Turnkey tools <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### Updating README.md files via multimd <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The `90-update-READMEs.py` script searches for `readme` folders. For each folder found, the `Python` module `multimd` is invoked to generate a single `README.md` file alongside the `readme` folder.

<a id="MULTIMD-TOC-ANCHOR-4"></a>
### Contribution file documentation <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

The directory structure of the `contrib` folder is specified in the `contrib/README.md` file. The script
`01-contrib/90-README-folders-struct.py` is designed to update this printed structure automatically.

<a id="MULTIMD-TOC-ANCHOR-5"></a>
Some basic utilities <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
--------------------

The `tools/cbutils` folder is a "local" module for specific scripts intended for use by several tools (never forget the `DRY` principle). It contains the `core` submodule, which brings together some very commonly used tools.

---

> ***NOTE.*** *The file `tools/cbutils/core/MANUAL.md` provides a quick overview of the `core` submodule.*

---

> ***WARNING!*** *If you think the `core` submodule could be improved, please submit your suggestions via the `copier-templates` project at https://github.com/projetmbc/copier-templates. You will have to change the folder `tools/cbutils/core` of the repository, and not of the template.*

---

> ***TIP.*** *Let's assume that the file `my-tool.py` is located directly in the `tools` folder. The `cbutils` package can be imported in a somewhat inelegant but functional manner, as follows.*

~~~python
#!/usr/bin/env python3

from pathlib import Path
import sys

# We go back as many levels as necessary via the `parent` attribute
# (just one level in our case).
TOOLS_DIR = Path(__file__).parent

# `sys.path` is a list of strings.
sys.path.append(str(TOOLS_DIR))

# Now everything works as if we had installed the `cbutils` package.
import cbutils

# This is where your coding begins.
...
~~~
