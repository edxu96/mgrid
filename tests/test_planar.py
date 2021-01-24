"""Test class in ``planar.py``."""
import networkx as nx
import pandas as pd

from mgrid.planar import COLUMNS, PlanarGraph


def test_init():
    """Check if a planar graph can be initiated from a directed graph."""
    dg = nx.DiGraph()
    dg.add_edge("a", "b", layer=0)
    dg.add_edge("a", "c", layer=-1)

    res = PlanarGraph(dg)
    assert list(res.inter_nodes.columns) == COLUMNS


def test_from_edgelist():
    """Check if a planar graph can be initiated from an edgelist."""
    df = pd.DataFrame(
        {"source": ["a", "a"], "target": ["b", "c"], "layer": [0, -1]}
    )

    res = PlanarGraph.from_edgelist(df, source="source", target="target")
    assert list(res.inter_nodes.columns) == COLUMNS
