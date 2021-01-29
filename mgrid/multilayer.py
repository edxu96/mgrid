"""Class for modelling power grid as multilayer graph."""
from typing import Optional

import networkx as nx


class MultilayerGrid:
    """Power grid with multiple voltage levels as multilayer network."""

    def __init__(self):
        """Initiate an empty network."""
        pass


class SupraGrid(nx.DiGraph):
    """Power grid with multiple voltage levels as supra-graph.

    Supra-graph is way to represent a multilayer network in one graph.
    Especially, intra-edges and inter-edges exist at the same time,
    while there is no inter-edge in :class:`planar.PlanarGrid`.

    Note:
        Any terminal pair of inter-edges is replica nodes. In planar
        graph, the inter-edge is contracted, so such two replica nodes
        are represented by one node. So they are called inter-nodes.
        Nodes in another kind only exist in one layer, and there is
        nothing in another lay related to them.

    Warning:
        It is impossible to modify ``MultilayerGrid`` for now, and it
        is frozen using ``networkx``.

    Attributes:
        intra_edges (DataFrame): correspondence between intra-edges in
            planar graph and in multilayer graph.

            ===============  =======  ======================  ==========
            name             dtype    definition              is_index
            ===============  =======  ======================  ==========
            source_original  object   source in planar graph  True
            target_original  object   target in planar graph  True
            source           object   current source bus      False
            target           object   current target bus      False
            ===============  =======  ======================  ==========

        inter_edges (DataFrame): correspondence between inter-nodes in
            planar graph and inter-edges in multilayer graph.

            ======  =======  ============================  ==========
            name    dtype    definition                    is_index
            ======  =======  ============================  ==========
            node    object   name in planar graph          True
            upper   int64    integer index of upper layer  False
            lower   int64    integer index of lower layer  False
            source  object   source node in supra graph    False
            target  object   target node in supra graph    False
            ======  =======  ============================  ==========

        nodelist (DataFrame): sorted nodelist containing layer
            information.

            ======  =======  ======================  ==========
            name    dtype    definition              is_index
            ======  =======  ======================  ==========
            name    object   node name               True
            layer   int64    integer index of layer  False
            ======  =======  ======================  ==========

    """

    def __init__(self, dg: Optional[nx.DiGraph] = None):
        """Init an empty directed graph or existing directed graph.

        Note:
            It is essential to have the option for empty graph, or some
            built-in ``networkx`` function will not work. Don't know
            why.

        Args:
            dg: an existing directed graph. Default to be None.
        """
        if not dg:
            super().__init__()
        else:
            super().__init__(dg)

        nx.freeze(self)

        self.intra_edges = None
        self.inter_edges = None
        self.nodelist = None
