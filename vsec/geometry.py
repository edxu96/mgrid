"""Classes and functions to build planar geometric graph.

Geographically, some edges might look like points. They can be
contracted to nodes.

"""
from typing import Optional

import networkx as nx
from vsec.graph import WeightGraph


class GeoGraph(WeightGraph):
    """Planar geometric graph with geographical information."""

    def __init__(self, g: Optional[nx.Graph] = None):
        """Init an empty directed graph or existing directed graph.

        Args:
            g: an existing directed graph. Default to be None.
        """
        if not g:
            super().__init__()
        else:
            super().__init__(g)
