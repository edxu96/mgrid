"""A class for two operations at the same time."""
from typing import Callable, Optional, Tuple, Union

from loguru import logger
import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame

COLUMNS = ["first", "second"]
COLUMNS_POS = ["node", "x", "y"]


class Graph(nx.DiGraph):
    """Graph with vertices to be split and edges to be contracted.

    Two methods ``merge_raw`` and ``merge_new`` are handy for
    transforming dataframes for curves and points respectively.

    Note:
        - Edges don't have name in ``networkx``.
    """

    def __init__(self, g: Optional[nx.DiGraph] = None):
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

        # Initiate dataframe **raw** for edges in the original edge.
        idx = pd.MultiIndex.from_tuples(self.edges, names=COLUMNS)
        self.raw = pd.DataFrame(
            data={
                "first": idx.get_level_values(0),
                "second": idx.get_level_values(1),
            },
            index=idx,
        )

    def split(
        self,
        vertex: str,
        first: str,
        second: str,
        attr: str,
        is_first: Callable[[str], Union[bool, None]],
    ):
        """Split a vertex and handle new vertices and associated edges.

        Warning:
            Only one edge attribute can be used to distinguish
            associated edges to two clusters.

        Args:
            vertex: which ought to be modelled as an edge.
            first: the first resulted vertex.
            second: the second resulted vertex.
            attr: edge attribute used as input in ``is_first``.
            is_first: how to choose between resulted vertices. When None
                is returned, an error will be logged.
        """
        # Find all the associated edges.
        edges_asso = list(self.in_edges(nbunch=vertex, data=True)) + list(
            self.out_edges(nbunch=vertex, data=True)
        )

        # Rename terminals of associated edges.
        for u, v, attributes in edges_asso:
            if is_first(attributes[attr]) is None:
                vertex_new = None
            elif is_first(attributes[attr]):
                vertex_new = first
            else:
                vertex_new = second

            if vertex_new:
                self.remove_edge(u, v)

                # Find the only corresponding edge in the initiated graph.
                index_origin = self.raw.index[
                    (self.raw["first"] == u) & (self.raw["second"] == v)
                ]
                assert len(index_origin) == 1, (
                    "The corresponding edge "
                    f"{index_origin.to_flat_index().tolist()} is not correct."
                )

                if u == vertex:
                    self.add_edge(vertex_new, v, **attributes)

                    new_column = pd.Series(
                        [vertex_new], name="first", index=index_origin
                    )
                    self._renamed_dict[(u, v)] = (vertex_new, v)
                else:
                    self.add_edge(u, vertex_new, **attributes)
                    new_column = pd.Series(
                        [vertex_new], name="second", index=index_origin
                    )
                    self._renamed_dict[(u, v)] = (u, vertex_new)

                self.raw.update(new_column)
            else:
                logger.critical(
                    f"Unable to determine new terminal of edge ({u}, {v}) "
                    f"with attributes {attributes}."
                )
                break

        # Validate if all associated edges have been renamed.
        edges_asso = list(self.edges(nbunch=vertex, data=True))
        assert len(edges_asso) == 0

        # Add the resulted new edge and remove the original vertex.
        self.add_edge(first, second, split_=True)
        self.remove_node(vertex)  # Removes the node and all adjacent edges.
        self._new_dict[vertex] = (first, second)

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
        """Gather renamed edges compared to initial graph.

        Returns:
            Edges renamed because of split or contraction.
        """
        res = pd.DataFrame.from_dict(
            self._renamed_dict, columns=COLUMNS, orient="index",
        )
        res.index = pd.MultiIndex.from_tuples(res.index, names=COLUMNS)
        return res

    def merge_raw(self, right: DataFrame, right_on: Tuple[str, str]):
        """Merge columns from another dataframe for original edges.

        Args:
            right: another dataframe with at least two separate columns
                specifying **source** and **target** of some original
                edges.
            right_on: names of those two columns corresponding to
                **source** and **target**.

        Returns:
            Dataframe for original edges with more columns merged. Two
            columns specified by **right_on** are not included.
        """
        return pd.merge(
            left=self.raw,
            right=right,
            left_index=True,
            right_on=right_on,
            how="left",
        )

    def merge_new(self, right: DataFrame):
        """Merge other columns for new edges (already-split vertices).

        Args:
            right: another dataframe with index being names of
                already-split vertices.

        Returns:
            Dataframe for original edges with more columns merged.
        """
        return pd.merge(
            left=self.new_,
            right=right,
            left_index=True,
            right_index=True,
            how="left",
        )

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

    @property
    def is_connected_graph(self) -> bool:
        """Check if this undirected graph is connected.

        Returns:
            True if this undirected graph is connected.
        """
        return nx.is_connected(self.to_undirected())
