# `mgrid`: multilayer network for power grid

[![GitHub license](https://img.shields.io/github/license/edxu96/mgrid)](./LICENSE) [![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![poetry](https://img.shields.io/badge/PyPM-poetry-5975aa)](https://python-poetry.org) ![mgrid](https://github.com/edxu96/mgrid/workflows/mgrid/badge.svg?branch=main)

A power grid with multiple voltage levels can be modelled using a
multilayer network. A graph in each layer represents all the cables in
the same voltage level. A directed bipartite for a pair of adjacent
layers represents transformers connecting two voltage levels.

There are two kinds of edges in multilayer network. Any intra-edge can
only exist in a single layer, and correspond to cables. Inter-edges
connect layers, and correspond to transformers.

There are more features when modelling power grid as multilayer network:

- At least one inter-edge connecting upper layer for a component
- No pair of planar nodes share the same name. That is, there is no
  replica of planar nodes, the setting of which is quite different from
  prototypical multilayer networks.
- Inter-edges exist between adjacent layers, and direct towards lower
  layers.
- There is geographical information associated with intra-edges, but not
  with inter-edges.
- All the inter-edges represent transformers.
- Terminals of any inter-edges are unique. Put another way, there is no
  pair of inter-edges sharing a terminal.

---

- [Documentation website](https://edxu96.github.io/mgrid/).
- Mainly based on: Bianconi, G. (2018). Multilayer networks: structure
  and function. Oxford university press.
