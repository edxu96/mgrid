"""Test class in ``planar.py``."""
from typing import Tuple

import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame
import pytest as pt

from mgrid.planar import COLUMNS, PlanarGraph, PlanarGrid
from mgrid.power_flow.element import Cable, Ejection, TransformerStd

COLUMNS_CABLE = ["from_node", "to_node", "layer"]
COL_TRANS = ["name", "type", "layer"]


@pt.fixture(scope="module")
def simple() -> PlanarGraph:
    """Init a planar graph from a directed graph.

    Returns:
        A simple planar graph with two intra-edges and one inter-edge.
    """
    dg = nx.DiGraph()
    dg.add_edge("a", "b", layer=0)
    dg.add_edge("a", "c", layer=1)

    res = PlanarGraph(dg)
    assert list(res.inter_nodes.columns) == COLUMNS
    assert res.inter_nodes.index.name == "name"
    assert res.layers == {0, 1}
    assert len(res.edges) == 2
    return res


def test_from_edgelist():
    """Check if a planar graph can be initiated from an edgelist."""
    df = pd.DataFrame(
        {"source": ["a", "a"], "target": ["b", "c"], "layer": [0, -1]}
    )

    res = PlanarGraph.from_edgelist(df, source="source", target="target")
    assert list(res.inter_nodes.columns) == COLUMNS


def test_methods(simple: PlanarGraph):
    """Check methods, properties, and attributes.

    Args:
        simple: A simple planar graph with two intralinks.
    """
    edges_layer_0 = simple.layer_edges(0)
    assert isinstance(edges_layer_0, DataFrame)

    graph_0 = simple.layer_graph(0)
    assert isinstance(graph_0, nx.DiGraph)


def test_planar_grid(data_grid: Tuple[DataFrame, DataFrame]):
    """Check if a planar grid can be initiated correctly.

    Args:
        data_grid: two dataframes for cables and nodes for a power grid.
    """

    def pass_cable_parameters(row):
        return Cable(
            length_km=row["len_km"],
            r_ohm_per_km=row["r_ohm_per_km"],
            x_ohm_per_km=row["x_ohm_per_km"],
            c_nf_per_km=row["c_nf_per_km"],
            max_i_ka=row["max_i_ka"],
        )

    cables = data_grid[0].loc[:, COLUMNS_CABLE].copy()
    cables["element"] = data_grid[0].apply(pass_cable_parameters, axis=1)

    planar = PlanarGrid.from_edgelist(
        cables, "from_node", "to_node", "element"
    )

    assert planar.layers == {1, 2}
    assert list(planar.inter_nodes.columns) == COLUMNS + ["element"]

    # Check if inter-nodes can be specified.
    planar.add_inter_node("EVO_6777175", TransformerStd("test"))
    planar.add_inter_node("EVO_2100520", TransformerStd("test"), upper=False)
    assert planar.find_layer("EVO_2100520") == (1, 2)

    # Check if inter-nodes are specified correctly.
    inter_nodes = data_grid[1].loc[
        data_grid[1]["layer"].isin([0.5, 1.5]), COL_TRANS
    ]
    assert set(planar.inter_nodes.index) == set(inter_nodes["name"])

    assert planar.intra_nodes.shape == (174, 1)
    assert planar.intra_nodes.index.name == "name"

    # Check dataframe for conversion elements.
    assert list(planar.conversion.columns) == ["node", "element", "layer"]
    assert planar.conversion.index.name == "name"
    planar.add_conversion("test", "EVO_2100520", Ejection(0, 0))
