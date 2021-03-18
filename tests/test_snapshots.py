"""Test class in ``snapshots/relational-db.py``."""

from mgrid.snapshots.relational import GraphSnapshots


def test_init():
    """Test relational database for snapshots of a graph."""
    gs = GraphSnapshots(":memory:")
    gs.add("a", "b", 0)
    gs.branch("test")
