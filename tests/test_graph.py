"""Test class in ``graph.py``."""
import networkx as nx
from pandas.core.frame import DataFrame
import pytest as pt
from vsec.graph import COLUMNS, Graph

ATTR = "level"
IS_FIRST = lambda x: x == "high"
EDGES_NEW = {
    ("a", "g_hv"),
    ("g_hv", "a"),
    ("c", "g_hv"),
    ("g_hv", "c"),
    ("d", "g_lv"),
    ("g_lv", "d"),
    ("f", "g_lv"),
    ("g_lv", "f"),
    ("g_lv", "g_hv"),
    ("g_hv", "g_lv"),
}


@pt.mark.usefixtures("case_readme")
def test_split(case_readme: nx.Graph):
    """Check basic features of ``split`` method in ``GeoGraph``.

    Note:
        ``split`` method is not tested thoroughly here.

    Args:
        case_readme: the test case shown in README file.
    """
    res = Graph(case_readme)
    res.split("g", "g_hv", "g_lv", ATTR, IS_FIRST)

    assert (
        set(res.edges).difference(EDGES_NEW) == set()
    ), "Terminals of associated edges should be renamed correctly."
    assert nx.is_connected(res)

    _new = res.new_
    assert isinstance(_new, DataFrame)
    assert _new.shape == (1, 2)
    assert list(_new.columns) == COLUMNS

    _renamed = res.renamed_
    assert isinstance(_renamed, DataFrame)
    assert _renamed.shape == (4, 2)
    assert list(_renamed.columns) == COLUMNS
    assert list(_renamed.index.names) == COLUMNS
