"""Test class in ``planar.py``."""
import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame
import pytest as pt

from mgrid.planar import COLUMNS, PlanarGrid
from .test_supra import Column, Index, print_columns

INTER = pd.DataFrame(
    [
        Index("node", "object", "name in planar graph"),
        Column("upper", "int64", "connected upper layer"),
        Column("lower", "int64", "connected lower layer"),
    ]
)


def test_print_columns():
    """Print columns of dataframes."""
    print_columns(INTER)


@pt.fixture(scope="module")
def simple() -> PlanarGrid:
    """Init a planar graph from a directed graph.

    Returns:
        A simple planar graph with two intra-edges and one inter-edge.
    """
    dg = nx.DiGraph()
    dg.add_edge("a", "b", layer=0)
    dg.add_edge("a", "c", layer=1)

    res = PlanarGrid(dg)
    assert list(res.inter_nodes.columns) == COLUMNS
    assert res.inter_nodes.index.name == "node"
    assert res.layers == {0, 1}
    assert len(res.edges) == 2
    return res


def test_from_edgelist():
    """Check if a planar graph can be initiated from an edgelist."""
    df = pd.DataFrame(
        {"source": ["a", "a"], "target": ["b", "c"], "layer": [0, -1]}
    )

    res = PlanarGrid.from_edgelist(df, source="source", target="target")
    assert list(res.inter_nodes.columns) == COLUMNS


def test_methods(simple: PlanarGrid):
    """Check methods, properties, and attributes.

    Args:
        simple: A simple planar graph with two intralinks.
    """
    edges_layer_0 = simple.layer_edges(0)
    assert isinstance(edges_layer_0, DataFrame)

    graph_0 = simple.layer_graph(0)
    assert isinstance(graph_0, nx.DiGraph)
