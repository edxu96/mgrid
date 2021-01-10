"""Class and function to build weighted graph.

There are two elements, nodes and weighted undirected edges.

"""
from typing import Optional

from loguru import logger
import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame


class WeightGraph(nx.Graph):
    """Mutable objects for directed graph with geographical information."""

    _col_edges = ['source', 'target']
    _col_pos = ['node', 'x', 'y']

    def __init__(self, g: Optional[nx.DiGraph] = None):
        """Init an empty directed graph or existing directed graph.

        Args:
            g: an existing directed graph. Default to be None.
        """
        if not g:
            super().__init__()
        else:
            super().__init__(g)

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
        dat[self._col_pos[0]] = list(self.nodes)  # Get names of all nodes.
        for col in self._col_pos[1:]:
            if self.complete_node_attr(col):
                dat[col] = [
                    self.nodes[node][col] for node in dat[self._col_pos[0]]
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
                f'There are {num_nodes - len(dict_node_attr)} nodes '
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
                f'There are {num_edges - len(dict_edge_attr)} edges '
                f'without the attribute "{attr}".'
                )
            res = False
        return res
