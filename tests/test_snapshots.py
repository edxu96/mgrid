"""Test class in ``snapshots/relational-db.py``."""

from mgrid.snapshots.relational import GraphSnapshots


def test_init():
    """Test relational database for snapshots of a graph."""
    gs = GraphSnapshots(":memory:")
    gs.add_edge("a", "b", 0)

    gs.branch("test", "head")
    print(gs._select_direct_links("test"))
    gs.read("test")
