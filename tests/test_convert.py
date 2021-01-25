"""Test functions in ``convert.py``."""
from itertools import chain

from mgrid.convert import COLUMNS_DI_ORIGINAL, planar2multilayer
from mgrid.planar import COLUMNS, COLUMNS_DI, PlanarGraph


def test_planar2multilayer(simple: PlanarGraph):
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

    inter_edges = res.inter_edges
    assert list(inter_edges.columns) == COLUMNS
    assert inter_edges.index.name == "node"


def test_case_grid(case_grid: PlanarGraph):
    """Check the case with 208 intra-edges and 34 inter-edges.

    Args:
        case_grid: the case with 208 intra-edges and 34 inter-edges.
    """
    res = planar2multilayer(case_grid)
    assert res.inter_edges.shape == (35, 2)
    assert res.number_of_edges() == 208 + 35
