"""Test functions in ``conversion.py``."""
import networkx as nx
import pytest as pt
from vsec.conversion import contract
from vsec.geometry import GeoGraph

# There are only two edges left, but sequences might be different.
EDGES = {("n1", "n2n3"), ("n2n3", "n1"), ("n2n3", "n4"), ("n4", "n2n3")}


@pt.mark.usefixtures("case_simple")
def test_contract(case_simple: nx.Graph):
    """Check if edge in a graph contracted and its terminals renamed.

    Args:
        case_simple: a simple graph with 3 edges.
    """
    res = contract(case_simple, "contraction")
    print(res.nodes)
    assert type(res) is GeoGraph
    assert set(res.edges).difference(EDGES) == set()
