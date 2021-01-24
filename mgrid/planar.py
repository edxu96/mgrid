"""A class for planar graph corresponding to a multilayer network."""
from itertools import chain
from typing import Optional

import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame

from mgrid.log import LOGGER

COLUMNS = ["upper", "lower"]


class PlanarGraph(nx.DiGraph):
    """Model multilayer network as planar graph."""

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
                    f"Incorrect specification for node {node} with max layer "
                    f"{upper} and min layer {lower}."
                )

        res = pd.DataFrame.from_dict(res_dict, orient="index", columns=COLUMNS)
        return res

    @classmethod
    def from_edgelist(
        cls,
        df: DataFrame,
        source: str,
        target: str,
        edge_attr: Optional[str] = "layer",
    ):
        """Init a planar graph from an edgelist dataframe.

        Args:
            df: an edgelist with at least three columns.
            source: column name indicating sources of edges.
            target: column name indicating targets of edges.
            edge_attr: column name indicating layers of edges. Default
                to be "layer".

        Returns:
            PlanarGraph
        """
        if (source not in df) or (target not in df) or (edge_attr not in df):
            LOGGER.critical(
                f"Column {source} or {target} not found in dataframe."
            )
            res = None
        else:
            res = nx.from_pandas_edgelist(
                df,
                source=source,
                target=target,
                edge_attr=edge_attr,
                create_using=nx.DiGraph(),
            )
            res = cls(res)
        return res

    @property
    def planar_nodes(self) -> DataFrame:
        """Gather all the planar nodes in a dataframe."""
        pass
