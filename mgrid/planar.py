"""A class for planar graph corresponding to a multilayer network."""
from itertools import chain
from typing import Optional, Set

import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame

from mgrid.log import LOGGER

COLUMNS = ["upper", "lower"]
COLUMNS_DI = ["source", "target"]


class PlanarGraph(nx.DiGraph):
    """Model multilayer network as planar graph.

    All the edges are intra-edges, so they must be associated with some
    layer. There are two kinds of nodes.

    Attributes:
        inter_nodes (DataFrame): all the inter-nodes, with two columns,
            "upper" and "lower".
        layers (Set[int]): integer indices of all the layers.
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

        self.inter_nodes = self._find_inter_nodes()

        # Find integer indices of all the layers.
        edgelist = nx.to_pandas_edgelist(self)
        if "layer" in edgelist:
            max_layer = edgelist["layer"].max()
            min_layer = edgelist["layer"].min()
            self.layers = set(range(min_layer, max_layer + 1))
        else:
            self.layers = set()

    def _find_inter_nodes(self) -> DataFrame:
        """Find all the inter-nodes.

        Returns:
            Dataframe with two columns, "upper" and "lower".
        """
        res_dict = {}
        for node in self.nodes:
            layers = [
                layer
                for _, _, layer in chain(
                    self.in_edges(node, data="layer"),
                    self.out_edges(node, data="layer"),
                )
            ]
            upper = max(layers)
            lower = min(layers)

            if upper == lower + 1:
                res_dict[node] = [upper, lower]
            elif upper == lower:
                pass
            else:
                LOGGER.warning(
                    f"Incorrect specification for node {node} corresponding "
                    f"to an inter-edge with max layer {upper} and min layer "
                    f" {lower}."
                )

        res = pd.DataFrame.from_dict(res_dict, orient="index", columns=COLUMNS)
        return res

    @classmethod
    def from_edgelist(
        cls, df: DataFrame, source: str, target: str,
    ):
        """Init a planar graph from an edgelist dataframe.

        Args:
            df: an edgelist with at least three columns.
            source: column name indicating sources of edges.
            target: column name indicating targets of edges.

        Returns:
            A ``PlanarGraph`` when the dataframe have essential columns.
        """
        if (source not in df) or (target not in df):
            LOGGER.critical(
                f"Column {source} or {target} not found in dataframe."
            )
            res = None
        else:
            res = nx.from_pandas_edgelist(
                df,
                source=source,
                target=target,
                edge_attr="layer",
                create_using=nx.DiGraph(),
            )
            res = cls(res)
        return res

    @property
    def planar_nodes(self) -> DataFrame:
        """Gather all the planar nodes in a dataframe."""
        pass

    def layer_edges(self, layer: int) -> Set[tuple]:
        """Gather all the edges and edge attributes in one layer.

        Args:
            layer: integer index of a layer.

        Returns:
            An edgelist for those in one layer.
        """
        if layer in self.layers:
            edge_list = nx.to_pandas_edgelist(self)
            res = edge_list[edge_list["layer"] == layer]
        else:
            res = None
        return res

    def layer_graph(self, layer: int) -> nx.DiGraph:
        """Build a directed graph for one layer.

        Note:
            Nodes corresponding to inter-edges are not distinguished in
            different layers.

        Args:
            layer: integer index of a layer.

        Returns:
            A directed graph representing a given layer.
        """
        if layer in self.layers:
            edges = self.layer_edges(layer)
            ite_edges = edges[COLUMNS_DI].itertuples(index=False, name=None)
            res = self.edge_subgraph(ite_edges).copy()
        else:
            res = None
        return res
