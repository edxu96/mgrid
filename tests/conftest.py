"""Configure unit tests in ``vsec``."""
import networkx as nx
import pandas as pd
import pytest as pt

from mgrid.graph.planar import COLUMNS, PlanarGraph


@pt.fixture(scope="module")
def simple() -> PlanarGraph:
    """Init a planar graph from a directed graph.

    Returns:
        A simple planar graph with two intra-edges and one inter-edge.
    """
    dg = nx.DiGraph()
    dg.add_edge("a", "b", layer=0)
    dg.add_edge("a", "c", layer=1)

    res = PlanarGraph(dg)
    assert list(res.inter_nodes.columns) == COLUMNS
    assert res.inter_nodes.index.name == "name"
    assert res.layers == {0, 1}
    assert len(res.edges) == 2
    return res


@pt.fixture(scope="package")
def case_large() -> PlanarGraph:
    """Init a case with 8 planar edges and 2 inter-edges.

    Returns:
        A test case with 8 planar edges and 2 inter-edges.
    """
    df = pd.read_csv("./tests/planar_large.csv")
    res = PlanarGraph.from_edgelist(df, "source", "target")
    res.add_inter_node("n3", upper=False)

    assert res.number_of_edges() == 8
    assert res.number_of_nodes() == 7
    return res
