"""Test functions in ``conversion.py``."""
import networkx as nx
from pandas.core.frame import DataFrame
import pytest as pt
from vsec.conversion import contract, split
from vsec.geometry import GeoGraph

# There are only two edges left, but sequences might be different.
EDGES = {("n1", "n2n3"), ("n2n3", "n1"), ("n2n3", "n4"), ("n4", "n2n3")}

# Arguments used to split multiple vertices in ``case_grid``.
ATTR = "voltage"
NAMING = lambda x: (x + "_hv", x + "_lv")
IS_FIRST = lambda x: x == 10

# Two columns in dataframe for resulted new vertices.
COLUMNS = {"first", "second"}


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


@pt.mark.usefixtures("case_grid", "vertices_grid")
def test_split(case_grid: GeoGraph, vertices_grid: DataFrame):
    """Check if all 10-0.4 kV transformers can be split.

    Note:
        - The result is not tested thoroughly.
        - The only 60-10 kV transformer is not split here.

    Args:
        case_grid: a case with 207 edges.
        vertices_grid: vertices in ``case_grid`` and their **type**
            attributes.
    """
    vertices_split = vertices_grid.index[vertices_grid["type"] == "STAT1004"]
    graph, vertex_df = split(case_grid, vertices_split, NAMING, ATTR, IS_FIRST)

    assert isinstance(nx.to_pandas_edgelist(graph), DataFrame)
    assert nx.is_connected(graph)
    assert isinstance(vertex_df, DataFrame)
    assert vertex_df.index.name == "original"
    assert set(vertex_df.columns) == COLUMNS
