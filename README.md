# `vsec`: vertex splitting & edge contraction

[![GitHub license](https://img.shields.io/github/license/edxu96/vsec)](./LICENSE) [![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![poetry](https://img.shields.io/badge/PyPM-poetry-5975aa)](https://python-poetry.org)

`vsec` provides a data structure when some edges in a graph are planar
points in essence. It is short for .

```
a   d  --------------->  a             d
 \ /   Vertex Splitting   \           /
  g                        g_hv - g_lv
 / \   Edge Contraction   /           \
c   f  <---------------  c             f
```

It is used when we (at [Utiligize](https://www.utiligize.com/)) model
power grids in western Denmark. Transformers should be modelled as edges
in a graph representing the grid, but they are points geographically. On
the other hand, data on electrical devices like power plants is usually
associated with geographical points.

Additionally, there are some methods to handle `pandas` dataframes associated
with such two objects.

Terms originate from [david2009random] and [heggernes2014contracting].

## Why

- More validation.
- No redundant renaming operation on different dataframes.

## Reference

- David, F., Dukes, W. M. B., Jonsson, T., & Stefansson, S. O. (2009). Random
  tree growth by vertex splitting. Journal of Statistical Mechanics: Theory and
  Experiment, 2009(04), P04009.
- Heggernes, P., Van’t Hof, P., Lévêque, B., Lokshtanov, D., & Paul, C. (2014).
  Contracting graphs to paths and trees. Algorithmica, 68(1), 109-132.
