### The about.yaml file

This file defines the cleanup tasks for production deployment and the output formats to be generated. All available keys are listed below, followed by their detailed usage.

~~~yaml
modular   : ...
monolithic: ...

clean:
  data  : ...
  gobble: ...
~~~


By default, all formats are generated. If a technology cannot produce a specific format, use `monolithic: no` to omit all-in-one files, and `modular: no` to skip individualized files.


To clean up the contribution folder, the `gobble` sub-key allows to provide a list of gobble patterns using paths relative to the contribution root.
To simplify maintenance, the `data` sub-key adds the possibility to define virtual variables as lists of sub-patterns.
For instance, in the following dummy example, using `dev/luadraw/*.latex_temp_ext` is equivalent to specifying `dev/luadraw/*.aux` and `dev/luadraw/*.log`.

~~~yaml
clean:
  data:
    latex_temp_ext:
      - aux
      - log

  gobble:
    - dev/luadraw/*.\latex_temp_ext
~~~
