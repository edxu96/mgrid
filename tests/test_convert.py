"""Test functions in ``convert.py``."""
from itertools import chain

import networkx as nx

from mgrid.convert import COLUMNS_DI_ORIGINAL, planar2supra
from mgrid.planar import COLUMNS, COLUMNS_DI, PlanarGrid


def test_planar2supra(simple: PlanarGrid):
    """Check if a planar graph can be converted to supra-graph.

    Args:
        simple: a simple planar graph with two intra-edges and one
            inter-edge.
    """
    res = planar2supra(simple)

    assert nx.is_frozen(res)

    intra_edges = res.intra_edges
    assert list(intra_edges.index.names) == COLUMNS_DI_ORIGINAL
    assert all(
        col in intra_edges.columns for col in chain(COLUMNS_DI, ["layer"])
    )

    inter_edges = res.inter_edges
    assert list(inter_edges.columns) == COLUMNS + COLUMNS_DI
    assert inter_edges.index.name == "node"


def test_case_grid(case_grid: PlanarGrid):
    """Check the case with 208 intra-edges and 34 inter-edges.

    Args:
        case_grid: the case with 208 intra-edges and 34 inter-edges.
    """
    res = planar2supra(case_grid)

    assert nx.is_frozen(res)
    assert res.inter_edges.shape == (35, 4)
    assert res.number_of_edges() == 208 + 35
    assert res.nodelist.shape[0] == 244
