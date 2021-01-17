"""A class for two operations at the same time.

Any modification after the initiation should be avoided, or many methods
and properties will not work as expected.
"""
from typing import Callable, Optional, Set, Tuple, Union

from loguru import logger
import networkx as nx
from networkx.algorithms.minors import contracted_edge
from networkx.relabel import relabel_nodes
import pandas as pd
from pandas.core.frame import DataFrame

COLUMNS = ["first", "second"]
INDEX_NAMES = ["source_original", "target_original"]
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

        Note:
            It is essential to have the option for empty graph, or some
            built-in ``networkx`` function will not work. Don't know
            why.

        Args:
            g: an existing directed graph. Default to be None.
        """
        if not g:
            super().__init__()
        else:
            super().__init__(g)

        # Initiate dictionary to store already-split vertices.
        self._new_dict = {}

        # Initiate dataframe **raw** for edges in the original edge.
        idx = pd.MultiIndex.from_tuples(self.edges, names=INDEX_NAMES)
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
        source: str,
        target: str,
        attr: str,
        is_connect_source: Callable[[str], Union[bool, None]],
    ):
        """Split a vertex and handle new vertices and associated edges.

        Warning:
            For now, only one edge attribute can be used to distinguish
            associated edges to two clusters.

        Args:
            vertex: which ought to be modelled as an edge.
            source: the first resulted vertex.
            target: the second resulted vertex.
            attr: edge attribute used as input in ``is_first``.
            is_connect_source: if an associated edge should be connected
                to the resulted new vertex called **source**. When None
                is returned, an error will be logged.
        """
        in_edges = list(self.in_edges(nbunch=vertex, data=True))
        for u, v, data in in_edges:
            edge_original = self.raw.index[
                (self.raw["first"] == u) & (self.raw["second"] == v)
            ]
            self.remove_edge(u, v)
            if is_connect_source(data[attr]) is None:
                logger.critical(
                    f"Unable to determine new terminals of edge ({u}, {v}) "
                    f"with attributes {data}."
                )
            elif is_connect_source(data[attr]):
                self.add_edge(u, source, **data)
                self._update_raw((u, source), edge_original)
            else:
                self.add_edge(u, target, **data)
                self._update_raw((u, target), edge_original)

        out_edges = list(self.out_edges(nbunch=vertex, data=True))
        for u, v, data in out_edges:
            edge_original = self.raw.index[
                (self.raw["first"] == u) & (self.raw["second"] == v)
            ]
            self.remove_edge(u, v)
            if is_connect_source(data[attr]) is None:
                logger.critical(
                    f"Unable to determine new terminals of edge ({u}, {v}) "
                    f"with attributes {data}."
                )
            elif is_connect_source(data[attr]):
                self.add_edge(source, v, **data)
                self._update_raw((source, v), edge_original)
            else:
                self.add_edge(target, v, **data)
                self._update_raw((target, v), edge_original)

        # Validate if all associated edges have been updated.
        edges_asso = list(self.edges(nbunch=vertex, data=True))
        if len(edges_asso) != 0:
            logger.critical(
                f"There is still edge(s) {edges_asso} associated with "
                f"vertex {vertex}."
            )

        # Add the resulted new edge and remove the original vertex.
        self.add_edge(source, target)
        self.remove_node(vertex)  # Removes the node and all adjacent edges.
        self._new_dict[vertex] = (source, target)

    def _update_raw(self, edge_updated: str, edge_original: Tuple[str, str]):
        """Correspond updated edge to that in the original graph.

        Args:
            edge_updated: the edge after update.
            edge_original: the corresponding edge in the original graph.
        """
        self.raw.loc[edge_original, COLUMNS] = edge_updated

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
    def vertices_new(self) -> Set[str]:
        """Gather all the new vertices in a set.

        Returns:
            All the new vertices.
        """
        return set(self.new_[COLUMNS[0]].unique()) | set(
            self.new_[COLUMNS[1]].unique()
        )

    def find_vertices_component(self, vertex: str) -> Union[Set[str], None]:
        """Get a set for all the vertices in the same component.

        Args:
            vertex: a vertex in the graph (after splitting).

        Returns:
            A set of vertices or None if ``vertex`` is not the graph.
        """
        if vertex not in self.nodes:
            logger.error(f"Vertex {vertex} is not in the graph.")
            res = None
        else:
            g = self.with_cuts.to_undirected()
            res = nx.node_connected_component(g, vertex)
        return res

    @property
    def with_cuts(self) -> nx.DiGraph:
        """Get directed graph with all resulted edges being cuts.

        Note:
            According to ``networkx`` documentation, the graph, edge,
            and node attributes in the returned subgraph view are
            references to the corresponding attributes in the original
            graph. The view is read-only. To create a full graph version
            of the subgraph with its own copy of the edge or node
            attributes, use ``g.edge_subgraph().copy()``.

        Returns:
            A directed graph.
        """
        ite_edges = self.raw[COLUMNS].itertuples(index=False, name=None)
        dg = self.edge_subgraph(ite_edges).copy()
        return dg

    def merge_raw(
        self,
        right: DataFrame,
        right_on: Tuple[str, str],
        how: Optional[str] = "right",
    ):
        """Merge columns from another dataframe for original edges.

        Args:
            right: another dataframe with at least two separate columns
                specifying **source** and **target** of some original
                edges.
            right_on: names of those two columns corresponding to
                **source** and **target**.
            how: type of merge to be performed. See [pandas.merge]_.

        .. pandas.merge:
            https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge.html

        Returns:
            Dataframe for original edges with more columns merged. Two
            columns specified by **right_on** are not included.
        """
        return pd.merge(
            left=self.raw,
            right=right,
            left_index=True,
            right_on=right_on,
            how=how,
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

    def contract(
        self, attr: str, naming: Optional[Callable[[Tuple[str, str]], str]],
    ) -> nx.Graph:
        """Contract edges with ``attr`` being true in ``Graph``.

        Args:
            attr: some bool edge attribute indicating contraction if
                true.
            naming: a function to name the new node based on labels of
                two terminals of the contracted edge.

        Returns:
            A graph with less edge(s).
        """
        graph = nx.Graph(self)
        for u, v, attributes in self.edges(data=True):
            if attributes[attr]:
                edge_contracted = (u, v)
                graph = contracted_edge(
                    graph, edge_contracted, self_loops=False
                )
                logger.debug(f"Edge {edge_contracted} has been contracted.")

                # Find which node is kept.
                if u in graph.nodes:
                    mapping = {u: naming(edge_contracted)}
                else:
                    mapping = {v: naming(edge_contracted)}

                # Rename the kept node.
                relabel_nodes(graph, mapping, copy=False)

        return graph
