"""Test functions in ``convert.py``."""
from itertools import chain

from mgrid.graph.planar import COLUMNS, COLUMNS_DI, PlanarGraph
from mgrid.grid import PlanarGrid
from mgrid.transformation import COLUMNS_DI_ORIGINAL, planar2supra


def test_planar2supra(simple: PlanarGraph):
    """Check if a planar graph can be converted to supra-graph.

    Args:
        simple: a simple planar graph with two intra-edges and one
            inter-edge.
    """
    res = planar2supra(simple)

    intra_edges = res.intra_edges
    assert list(intra_edges.index.names) == COLUMNS_DI_ORIGINAL
    assert all(
        col in intra_edges.columns for col in chain(COLUMNS_DI, ["layer"])
    )

    inter_edges = res.inter_edges
    assert list(inter_edges.columns) == COLUMNS + COLUMNS_DI
    assert inter_edges.index.name == "node"


def test_case_large(case_large: PlanarGrid):
    """Check the case with 8 planar edges and 2 inter-edges.

    Args:
        case_large: a test case with 8 planar edges and 2 inter-edges.
    """
    res = planar2supra(case_large)
    assert res.number_of_edges() == 8 + 2
    assert res.number_of_nodes() == 7 + 2
