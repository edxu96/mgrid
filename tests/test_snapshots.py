"""Test class in ``snapshots/relational-db.py``."""

from mgrid.snapshots.relational import GraphSnapshots

EDGES_SNAPSHOT_3 = {("b", "c"), ("c", "d")}


def test_init():
    """Test relational database for snapshots of a graph."""
    gs = GraphSnapshots(":memory:")
    gs.add_edge("a", "b", 0)
    gs.add_edge("c", "b", 1)

    gs.pose("test", "head")
    gs._select_direct_links("test")


def test_manual_insertions():
    """Test methods in ``GraphSnapshots`` after some manual insertions."""
    gs = GraphSnapshots(":memory:")

    # Insert some values manually for the sack of tests.
    with gs.conn:
        gs.conn.executescript(
            """
            INSERT INTO snapshots (name)
            VALUES ('first'), ('second'), ('third');

            INSERT INTO edges (source, target, element)
            VALUES ('a', 'b', 1), ('b', 'c', 2), ('c', 'd', 3);

            INSERT INTO events (snapshot, source, target)
            VALUES
                ('first', 'a', 'b'), ('second', 'b', 'c'), ('third', 'c', 'd'),
                ('third', 'a', 'b');

            INSERT INTO links (snapshot, link)
            VALUES
                ('first', 'head'), ('second', 'head'), ('third', 'first'),
                ('third', 'second');
        """
        )

    assert gs.sym_diff({"first", "second", "third"}) == EDGES_SNAPSHOT_3
