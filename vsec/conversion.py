"""Functions to convert two different graphs."""
from typing import Callable, Optional, Tuple, Union

from loguru import logger
import networkx as nx
from networkx.algorithms.minors import contracted_edge
from networkx.relabel import relabel_nodes
from vsec.geometry import GeoGraph
from vsec.graph import WeightGraph


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


def split(graph: GeoGraph):
    """Split nodes.

    Args:
        graph (GeoGraph): [description]
    """
    pass
