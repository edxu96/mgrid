"""A class for two operations at the same time."""
from typing import Callable, Optional, Union

from loguru import logger
import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame

COLUMNS = ["first", "second"]
COLUMNS_POS = ["node", "x", "y"]


class Graph(nx.Graph):
    """Graph with vertices to be split and edges to be contracted.

    Note:
        - ``GeoGraph`` is based on ``WeightGraph`` class, so add their
          common features like ``df_edges`` and ``complete_edge_attr``
          in ``WeightGraph``.
        - Edges don't have name in ``networkx``.
    """

    def __init__(self, g: Optional[nx.Graph] = None):
        """Init an empty directed graph or existing directed graph.

        Args:
            g: an existing directed graph. Default to be None.
        """
        if not g:
            super().__init__()
        else:
            super().__init__(g)

        self._new_dict = {}
        self._renamed_dict = {}

    def split(
        self,
        vertex: str,
        vertex_first: str,
        vertex_second: str,
        attr: str,
        is_first: Callable[[str], Union[bool, None]],
    ):
        """Split a vertex and handle new vertices and associated edges.

        Args:
            vertex: which ought to be modelled as an edge.
            vertex_first: the first resulted vertex.
            vertex_second: the second resulted vertex.
            attr: edge attribute used as input in ``is_first``.
            is_first: how to choose between resulted vertices. When None
                is returned, an error will be logged.
        """
        edges_asso = list(self.edges(nbunch=vertex, data=True))

        # Rename terminals of associated edges.
        for u, v, attributes in edges_asso:
            if is_first(attributes[attr]) is None:
                vertex_new = None
            elif is_first(attributes[attr]):
                vertex_new = vertex_first
            else:
                vertex_new = vertex_second

            if vertex_new:
                self.remove_edge(u, v)
                if u == vertex:
                    self.add_edge(vertex_new, v, **attributes)
                    self._renamed_dict[(u, v)] = (vertex_new, v)
                else:
                    self.add_edge(u, vertex_new, **attributes)
                    self._renamed_dict[(u, v)] = (u, vertex_new)
            else:
                logger.critical(
                    f"Unable to determine new terminal of edge ({u}, {v}) "
                    f"with attributes {attributes}."
                )
                break

        # Add the resulted new edge and remove the original vertex.
        self.add_edge(vertex_first, vertex_second, split_=True)
        self.remove_node(vertex)
        self._new_dict[vertex] = (vertex_first, vertex_second)

    @property
    def new_(self) -> DataFrame:
        """Gather vertex and edge resulted from split or contraction.

        Returns:
            Vertex and edge resulted from split or contraction in
            sequence.
        """
        res = pd.DataFrame.from_dict(
            self._new_dict, columns=COLUMNS, orient="index",
        )
        res.index.name = "vertex"
        return res

    @property
    def renamed_(self) -> DataFrame:
        """Gather edges renamed because of split or contraction.

        Returns:
            Edges renamed because of split or contraction.
        """
        res = pd.DataFrame.from_dict(
            self._renamed_dict, columns=COLUMNS, orient="index",
        )
        res.index = pd.MultiIndex.from_tuples(res.index, names=COLUMNS)
        return res

    @property
    def df_edges(self) -> DataFrame:
        """Collect all edges and their attributes in a data frame.

        Returns:
            All the edges and their attributes in RDF.
        """
        return nx.to_pandas_edgelist(self)

    @property
    def df_nodes(self) -> DataFrame:
        """Collect all nodes and their attributes in a data frame.

        Returns:
            DataFrame: containing all nodes and their attributes.
        """
        dat = {}
        dat[self.COLUMNS_POS[0]] = list(self.nodes)  # Get names of all nodes.
        for col in self.COLUMNS_POS[1:]:
            if self.complete_node_attr(col):
                dat[col] = [
                    self.nodes[node][col] for node in dat[self.COLUMNS_POS[0]]
                ]
        return pd.DataFrame(dat)

    def complete_node_attr(self, attr: str) -> bool:
        """Check if all nodes in the graph have the given attribute.

        Args:
            attr: name of the attribute.

        Returns:
            True if all nodes in the graph have the given attribute.
        """
        res = True
        num_nodes = len(self.nodes)
        dict_node_attr = nx.get_node_attributes(self, attr)
        if len(dict_node_attr) < num_nodes:
            logger.exception(
                f"There are {num_nodes - len(dict_node_attr)} nodes "
                f'without the attribute "{attr}".'
            )
            res = False
        return res

    def complete_edge_attr(self, attr: str) -> bool:
        """Check if all edges in the graph have the given attribute.

        Args:
            attr: name of the attribute.

        Returns:
            True if all nodes in the graph have the given attribute.
        """
        res = True
        num_edges = len(self.edges)
        dict_edge_attr = nx.get_edge_attributes(self, attr)
        if len(dict_edge_attr) < num_edges:
            logger.exception(
                f"There are {num_edges - len(dict_edge_attr)} edges "
                f'without the attribute "{attr}".'
            )
            res = False
        return res
