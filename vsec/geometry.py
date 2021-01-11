"""Classes and functions to build planar geometric graph.

Geographically, some edges might look like points. They can be
contracted to nodes.

"""
from typing import Callable, Optional, Tuple, Union

from loguru import logger
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

    def split(
        self,
        vertex: str,
        naming: Callable[[str], Tuple[str, str]],
        attr: str,
        is_first: Callable[[str], Union[bool, None]],
    ) -> Tuple[str, str]:
        """Split a vertex and handle new vertices and associated edges.

        Args:
            vertex: a vertex ought to be modelled by an edge.
            naming: how two resulted vertices should be named.
            attr: edge attribute used as input in ``is_first``.
            is_first: how to choose between resulted vertices. When None
                is returned, an error will be logged.

        Returns:
            Two resulted vertices.
        """
        edges_asso = list(self.edges(nbunch=vertex, data=True))
        vertices = naming(vertex)
        for u, v, attributes in edges_asso:
            if is_first(attributes[attr]) is None:
                vertex_new = None
            elif is_first(attributes[attr]):
                vertex_new = vertices[0]
            else:
                vertex_new = vertices[1]

            if vertex_new:
                self.remove_edge(u, v)
                if u == vertex:
                    self.add_edge(vertex_new, v, **attributes)
                else:
                    self.add_edge(u, vertex_new, **attributes)
            else:
                logger.critical(
                    f"Unable to determine new terminal of edge ({u}, {v}) "
                    f"with attributes {attributes}."
                )
                vertices = None
                break

        return vertices
