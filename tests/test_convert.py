"""Test functions in ``convert.py``."""
from itertools import chain

from mgrid.convert import COLUMNS_DI_ORIGINAL, planar2multilayer
from mgrid.planar import COLUMNS_DI


def test_planar2multilayer(simple):
    """Check if a planar graph can be converted to multilayer graph.

    Args:
        simple: a simple planar graph with two intra-edges and one
            inter-edge.
    """
    res = planar2multilayer(simple)

    intra_edges = res.intra_edges
    assert list(intra_edges.index.names) == COLUMNS_DI_ORIGINAL
    assert all(
        col in intra_edges.columns for col in chain(COLUMNS_DI, ["layer"])
    )
