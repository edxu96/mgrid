"""Class for multilayer network in supra-graph format."""
from typing import Optional

import networkx as nx


class SupraGraph(nx.DiGraph):
    """Multilayer network as a supra graph.

    Supra-graph is way to represent a multilayer network in one graph.
    Especially, intra-edges and inter-edges exist at the same time. See
    [bianconi2018multilayer]_ for details.

    Note:
        Any terminal pair of inter-edges is replica nodes. In planar
        graph, the inter-edge is contracted, so such two replica nodes
        are represented by one node. So they are called inter-nodes.
        Nodes in another kind only exist in one layer, and there is
        nothing in another lay related to them.

    Warning:
        It is impossible to modify ``SupraGraph`` for now, and it is
        frozen using ``networkx``.

    Attributes:
        intra_edges (DataFrame): correspondence between intra-edges in
            planar graph and in multilayer graph.

            .. csv-table::
                :header: name, dtype, definition

                source_original (index), object, target in planar graph
                target_original (index), object, target in planar graph
                source, object, current source bus
                target, object, current target bus

        inter_edges (DataFrame): correspondence between inter-nodes in
            planar graph and inter-edges in multilayer graph.

            .. csv-table::
                :header: name, dtype, definition

                node (index), object, name in planar graph
                upper, int64, integer index of upper layer
                lower, int64, integer index of lower layer
                source, object, source node in supra graph
                target, object, target node in supra graph

        nodelist (DataFrame): sorted nodelist containing layer
            information.

            .. csv-table::
                :header: name, dtype, definition

                node (index), object, node name
                idx, int64, layer to which node belongs
                name, object, layer name
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

        # nx.freeze(self)

        self.intra_edges = None
        self.inter_edges = None
        self.nodelist = None