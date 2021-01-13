"""Test class in ``graph.py``."""
import networkx as nx
from pandas.core.frame import DataFrame
import pytest as pt
from vsec.graph import COLUMNS, Graph

ATTR = "level"
IS_FIRST = lambda x: x == "high"
EDGES_NEW = {
    ("a", "g_hv"),
    ("c", "g_hv"),
    ("d", "g_lv"),
    ("f", "g_lv"),
    ("g_hv", "g_lv"),
}


@pt.mark.usefixtures("case_readme")
def test_split(case_readme: nx.DiGraph):
    """Check basic features of ``split`` method in ``GeoGraph``.

    Note:
        ``split`` method is not tested thoroughly here.

    Args:
        case_readme: the test case shown in README file.
    """
    res = Graph(case_readme)
    res.split("g", "g_hv", "g_lv", ATTR, IS_FIRST)

    assert (
        set(res.edges) == EDGES_NEW
    ), "Terminals of associated edges should be renamed correctly."
    assert res.is_connected_graph

    _new = res.new_
    assert isinstance(_new, DataFrame)
    assert _new.shape == (1, 2)
    assert list(_new.columns) == COLUMNS

    raw = res.raw
    assert isinstance(raw, DataFrame)
    assert raw.shape == (4, 2)
    assert list(raw.columns) == COLUMNS
    assert list(raw.index.names) == COLUMNS

    with_cuts = res.with_cuts
    assert set(with_cuts.edges) == EDGES_NEW - {("g_hv", "g_lv")}
    assert isinstance(with_cuts, nx.Graph)

    assert res.find_vertices_component("g_hv") == {"g_hv", "a", "c"}
    assert res.find_vertices_component("g_lv") == {"g_lv", "d", "f"}
