Power Grid as Multilayer Network
================================

|license| |black| |poetry| |action|

.. |license| image:: https://img.shields.io/github/license/edxu96/mgrid
.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
.. |poetry| image:: https://img.shields.io/badge/PyPM-poetry-5975aa
.. |action| image:: https://github.com/edxu96/mgrid/workflows/mgrid/badge.svg?branch=main

A power grid with multiple voltage levels can be modelled using a
multilayer network. A graph in each layer represents all the cables in
the same voltage level. A directed bipartite for a pair of adjacent
layers represents transformers connecting two voltage levels.

There are two kinds of edges in multilayer network. Any intra-edge can
only exist in a single layer, and correspond to cables. Inter-edges
connect layers, and correspond to transformers in terms of power grids.

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

There are at least eight operations:

- Model a power grid as ``PlanarGrid`` using data on cables.
- Specify some planar nodes to be inter-nodes.
- Convert ``PlanarGrid`` to ``SupraGrid``.
- Get subgraph in one layer with some inter-nodes.
- Get all the nodes in one layer in ``SupraGrid``.
- Get subgraph in one layer in ``SupraGrid``.
- Select inter-nodes in ``PlanarGrid`` (inter-edges in ``SupraGrid``).
- Find layer of a node in ``PlanarGrid`` or ``SupraGrid``.

Three Representation Methods
----------------------------

======================================== =============== ===============
Python class                             intra-edge      inter-edge
======================================== =============== ===============
:class:`mgrid.graph.planar.PlanarGraph`  in planar graph contracted
:class:`mgrid.graph.supra.SupraGraph`    in planar graph in planar graph
                                         in layer        between layers
======================================== =============== ===============

Usually, datasets are stored with respect to ``PlanarGrid``, then all
the edges and nodes can have geographical information. When modelling,
it should be converted to ``SupraGrid``. As a result, all the nodes can
be seen as buses, and cables & transformers can have two terminals.

API
---

.. toctree::
   :maxdepth: 2

   graph
   grid
   power_flow
   transformation

Bibliography
------------

.. toctree::
   :maxdepth: 1

   bibliography
