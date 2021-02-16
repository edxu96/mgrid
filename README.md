# `mgrid`: Power Grid as Multilayer Network

[![GitHub license](https://img.shields.io/github/license/edxu96/mgrid)](./LICENSE) [![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![poetry](https://img.shields.io/badge/PyPM-poetry-5975aa)](https://python-poetry.org) ![mgrid](https://github.com/edxu96/mgrid/workflows/mgrid/badge.svg?branch=main)

`mgrid` is a pure Python package to model power grids as multilayer
networks. The number of voltage levels equals the number of layers. A
graph in each layer represents all the cables at the same voltage level.
A directed bipartite for a pair of adjacent layers represents
transformers connecting two voltage levels. Moreover, `mgrid` provides
an interface for power system analysis.

## Multilayer Network

There are two kinds of edges in a multilayer network. Any intra-edge can
only exist in a single layer and correspond to cables. Inter-edges
connect layers, and correspond to transformers.

There are some features worth mentioning when modelling power grids as
multilayer networks:

- At least one inter-edge connecting upper layer for a component
- No pair of planar nodes share the same name. That is, there is no
  replica of planar nodes, the setting of which is quite different from
  prototypical multilayer networks.
- Inter-edges exist between adjacent layers and direct towards lower
  layers.
- There is geographical information associated with intra-edges, but not
  with inter-edges.
- All the inter-edges represent transformers.
- Terminals of any inter-edges are unique. Put another way, there is no
  pair of inter-edges sharing a terminal.

## Interface for Power System Analysis

Electric devices can be modelled using built-in classes or customised
classes, then instance using supported Python packages for power system
analysis can be returned. Current, supported tools are:

- [`pandapower`](https://pandapower.readthedocs.io/en/stable/): combines
  the data analysis library pandas and the power flow solver PYPOWER to
  create an easy to use network calculation program aimed at automation
  of analysis and optimization in power systems.
- [`PyPSA`](https://pypsa.readthedocs.io/en/latest/index.html): a free
  software toolbox for simulating and optimising modern power systems
  that include features such as conventional generators with unit
  commitment, variable wind and solar generation, storage units,
  coupling to other energy sectors, and mixed alternating and direct
  current networks.

and supported studies are:

- Power flow calculation based on one-line-equivalent models for
  three-phase-four-wire power grids.
- Power flow calculation for unbalanced three-phase-four-wire power
  grids.
- Power flow calculation for unbalanced power grids with laterals
  (cables with less than three phases).

---

- [Documentation website](https://edxu96.github.io/mgrid/).
- Bianconi, G. (2018). Multilayer networks: structure and function.
  Oxford university press.
