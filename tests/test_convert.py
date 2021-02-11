"""Test functions in ``convert.py``."""
from itertools import chain

import networkx as nx

from mgrid.convert import COLUMNS_DI_ORIGINAL, planar2supra
from mgrid.planar import COLUMNS, COLUMNS_DI, PlanarGraph, PlanarGrid

_columns_inter_edges = ["upper", "lower", "source", "target"]
_columns_intra_edges = ["source", "target", "layer"]


def test_planar2supra(simple: PlanarGraph):
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


def test_grid(grid: PlanarGrid):
    """Check if ``PlanarGrid`` can be converted correctly.

    Args:
        grid: initiated planar grid.
    """
    res = planar2supra(grid)
    print(nx.to_pandas_edgelist(res))


def test_case_grid(case_grid: PlanarGraph):
    """Check the case with 208 intra-edges and 34 inter-edges.

    Args:
        case_grid: the case with 208 intra-edges and 34 inter-edges.
    """
    res = planar2supra(case_grid)

    assert nx.is_frozen(res)
    assert res.number_of_edges() == 208 + 35
    assert res.nodelist.shape == (244, 1)

    inter_edges = res.inter_edges
    assert res.inter_edges.shape == (35, 4)
    assert all(col in inter_edges for col in _columns_inter_edges)
    assert inter_edges.index.name == "node"

    intra_edges = res.intra_edges
    assert intra_edges.shape == (208, 3)
    assert all(col in intra_edges for col in _columns_intra_edges)
    assert intra_edges.index.names == ["source_original", "target_original"]


def test_case_large(case_large: PlanarGrid):
    """Check the case with 8 planar edges and 2 inter-edges.

    Args:
        case_large: a test case with 8 planar edges and 2 inter-edges.
    """
    res = planar2supra(case_large)
    assert res.number_of_edges() == 8 + 2
    assert res.number_of_nodes() == 7 + 2
