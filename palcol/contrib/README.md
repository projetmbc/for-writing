<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


Contribute to palcol
====================

**Table of contents**

<a id="MULTIMD-GO-BACK-TO-TOC"></a>
- [Where are the contributions?](#MULTIMD-TOC-ANCHOR-0)
- [Contribution workflow](#MULTIMD-TOC-ANCHOR-1)
    - [Start a new contribution](#MULTIMD-TOC-ANCHOR-2)
    - [Update one contribution](#MULTIMD-TOC-ANCHOR-3)
    - [Regular users of GitHub](#MULTIMD-TOC-ANCHOR-4)
- [Directory structure](#MULTIMD-TOC-ANCHOR-5)

<a id="MULTIMD-TOC-ANCHOR-0"></a>
Where are the contributions? <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
----------------------------

The contributions made are in the `contrib` folder which has the following structure.

<!-- FOLDER STRUCT. AUTO - START -->
~~~
+ contrib
~~~
<!-- FOLDER STRUCT. AUTO - END -->

<a id="MULTIMD-TOC-ANCHOR-1"></a>
Contribution workflow <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
---------------------

<a id="MULTIMD-TOC-ANCHOR-2"></a>
### Start a new contribution <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

Contributions are organised into folders, each of which contains a `README.md` file that explains how to contribute.

> ***IMPORTANT.*** *The contributions will necessarily be licensed under a* "GNU General Public License - Version 3" *license.*

<a id="MULTIMD-TOC-ANCHOR-3"></a>
### Update one contribution <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

If you wish to update a contribution proposal, you should quickly indicate in English the changes made and date them (no need to go into too much detail).

<a id="MULTIMD-TOC-ANCHOR-4"></a>
### Regular users of GitHub <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>

It is possible to use `git merge requests` to indicate one contribution.

<a id="MULTIMD-TOC-ANCHOR-5"></a>
Directory structure <a href="#MULTIMD-GO-BACK-TO-TOC" style="text-decoration: none;"><span style="margin-left: 0.25em; font-weight: bold; position: relative; top: -.5pt;">&#x2191;</span></a>
-------------------

The library `tools/cbutils/core` provides tools for managing contributions that comply with the specifications presented in this section.

The directory structure must be done as follows, where we note a similarity between the `one_feature` folder, which here would correspond to various contributions, and the `status` content folder of the `YAML` files indicating the status of each contribution (we will come back to these files shortly).

~~~
- contrib
    * README.md
    * LICENSE.txt
    - one_api
        + changes
        - one_feature
            * one_file.ext
            + one_module
        - status
            * one_file.yaml
            * one_module.yaml
~~~

The `status` folder is reserved for managing contribution statuses via `YAML` files that follow the format below.

~~~yaml
author: John, DOE

# Possible status.
#    - on hold
#    - ko
#    - ok
#    - update
status: on hold

# Classical comments.
#    - [on hold]  New API not yet analysed.
#                 Changes to do: ...
#    - [ko]       API rejected because ...
#    - [ok]       API accepted.
#    - [update]   Working on...
comment: New API not yet analysed.
~~~
