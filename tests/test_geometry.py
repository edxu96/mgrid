"""Test class in ``geometry.py``."""
import networkx as nx
import pytest as pt
from vsec.geometry import GeoGraph

ATTR = "level"
NAMING = lambda x: (x + "_hv", x + "_lv")
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
    gg = GeoGraph(case_readme)
    gg.split("g", NAMING, ATTR, IS_FIRST)

    assert (
        set(gg.edges).difference(EDGES_NEW) == set()
    ), "Terminals of associated edges should be renamed correctly."
