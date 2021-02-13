"""Test class in ``planar.py``."""
import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame

from mgrid.graph.planar import COLUMNS, PlanarGraph


def test_from_edgelist():
    """Check if a planar graph can be initiated from an edgelist."""
    df = pd.DataFrame(
        {"source": ["a", "a"], "target": ["b", "c"], "layer": [0, -1]}
    )

    res = PlanarGraph.from_edgelist(df, source="source", target="target")
    assert list(res.inter_nodes.columns) == COLUMNS


def test_methods(simple: PlanarGraph):
    """Check methods, properties, and attributes.

    Args:
        simple: A simple planar graph with two intralinks.
    """
    edges_layer_0 = simple.layer_edges(0)
    assert isinstance(edges_layer_0, DataFrame)

    graph_0 = simple.layer_graph(0)
    assert isinstance(graph_0, nx.DiGraph)
