<!----------------------------------------------------------------
  -- File created by the ''multimd'' project, version 1.0.0.    --
  --                                                            --
  -- ''multimd'', soon to be available on PyPI, is developed at --
  -- https://github.com/bc-tools/for-dev/tree/main/multimd      --
  ---------------------------------------------------------------->


The Python module palcol
========================

About palcol
------------

This project provides a collection of discrete color palettes for various programming languages,
enabling the creation and use of color maps derived from these palettes.

> ***CAUTION.*** *Only discrete palettes are provided. No continuous colormaps are implemented.*

Credits
-------

Many of the discrete color palettes in this project are based on colormaps from [`Asymptote`](https://asymptote.sourceforge.io/) and [`Matplotlib`](https://matplotlib.org/).
If you recognize your contribution, please don’t hesitate to get in touch, we’ll be happy to give you proper credit in the source code.

> ***IMPORTANT.*** *`colpal` only uses camel case names with no characters other than numbers and ASCII letters. For example, a name such as `nipy_spectral-1` is tranformed into `NipySpectral1` within `palcol`.*

Supported implementations
-------------------------

The implementations are inside the folder `products`.

### JSON, the versatile default format

By default, a file `products/palettes.json` is provided to allow unsupported coding languages to easily integrate palettes.
