Directory structure
-------------------

The library `tools/cbutils/core` provides tools for managing contributions that comply with the specifications presented in this section.

The directory structure must be done as follows, where we note a similarity between the `one_api` folder, which here would correspond to various contributions, and the `status` content folder of the `YAML` files indicating the status of each contribution (we will come back to these files shortly).

~~~
- contrib
    * README.md
    * LICENSE.txt
    - parser
        + changes
        - one_api
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
