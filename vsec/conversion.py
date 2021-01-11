"""Functions to convert two different graphs.

When to specify which vertices should be split, it is not recommended to
use some vertex attribute. Multiple sets of vertices can be passed.
Different arguments can be used each time accordingly.
"""
from typing import Callable, Optional, Set, Tuple, Union

from loguru import logger
import networkx as nx
from networkx.algorithms.minors import contracted_edge
from networkx.relabel import relabel_nodes
import pandas as pd
from pandas.core.frame import DataFrame
from vsec.geometry import GeoGraph
from vsec.graph import WeightGraph

COLUMNS = ["first", "second"]


def join_terminal_labels(edge: Tuple[str, str]) -> str:
    """Join labels of two terminals of a contracted edge.

    Args:
        edge: an edge to be contracted.

    Returns:
        Label of the new node.
    """
    if not (isinstance(edge[0], str) and isinstance(edge[0], str)):
        res = str(edge[0]) + str(edge[1])
        logger.warning("Some label is not string, which might be problematic.")
    else:
        res = edge[0] + edge[1]
    return res


def contract(
    graph: Union[WeightGraph, nx.Graph],
    attr: str,
    naming: Optional[Callable[[Tuple[str, str]], str]] = join_terminal_labels,
) -> GeoGraph:
    """Contract edges with ``attr`` being true in ``WeightGraph``.

    Args:
        graph: a weighted graph with some edges corresponding to
            geographical points.
        attr: some bool edge attribute indicating contraction if true.
        naming: a function to name the new node based on labels of two
            terminals of the contracted edge.

    Returns:
        The corresponding planar geometric graph.
    """
    for u, v, attributes in graph.edges(data=True):
        if attributes[attr]:
            edge_contracted = (u, v)
            graph = contracted_edge(graph, edge_contracted, self_loops=False)
            logger.debug(f"Edge {edge_contracted} has been contracted.")

            # Find which node is kept.
            if u in graph.nodes:
                mapping = {u: naming(edge_contracted)}
            else:
                mapping = {v: naming(edge_contracted)}

            # Rename the kept node.
            relabel_nodes(graph, mapping, copy=False)

    return GeoGraph(graph)


def split(
    graph: GeoGraph,
    vertices: Set[str],
    naming: Callable[[str], Tuple[str, str]],
    attr: str,
    is_first: Callable[[str], Union[bool, None]],
) -> Tuple[WeightGraph, DataFrame]:
    """Split multiple vertices of a planar geometric graph.

    Args:
        graph: a planar geometric graph with multiple vertex to be
            split.
        vertices: vertices ought to be modelled as edges.
        naming: how two resulted vertices should be named.
        attr: edge attribute used as input in ``is_first``.
        is_first: how to choose between resulted vertices. When None
            is returned, an error will be logged.

    Returns:
        Resulted weighted graph, and correspondence between split
        vertices & resulted new vertices.
    """
    vertex_dict = {}

    for vertex in vertices:
        vertex_dict[vertex] = graph.split(vertex, naming, attr, is_first)

    vertex_df = pd.DataFrame.from_dict(
        vertex_dict, orient="index", columns=COLUMNS,
    )
    vertex_df.index.name = "original"

    return graph, vertex_df
