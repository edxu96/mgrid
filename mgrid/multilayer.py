"""Class for modelling power grid as multilayer graph."""
from typing import Optional

import networkx as nx


class MultilayerGrid(nx.DiGraph):
    """Power grid with multiple voltage levels as multilayer graph.

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
            planar graph and in multilayer graph. The index has two
            levels, "source_original" and "target_original". There are
            at least three columns, "source", "target", and "layer".
        inter_edges (DataFrame): correspondence between inter-nodes in
            planar graph and inter-edges in multilayer graph. The index
            is "node", and two columns are "upper" & "lower".
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
