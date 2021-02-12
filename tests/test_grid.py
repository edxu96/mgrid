"""A real-world test case. Data has not been disclosed, yet."""
from copy import deepcopy
from typing import Tuple

import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame
import pytest as pt

from mgrid.convert import planar2supra
from mgrid.planar import COLUMNS, PlanarGraph, PlanarGrid
from mgrid.power_flow.delivery import Cable, TransformerStd
from mgrid.power_flow.pandapower import supra2pandapower
from mgrid.power_flow.type import TransformerType

# Dictionary to map entries in column "voltage" to layers.
VOLTAGES = {"04kv": 2, "10kv": 1, "60kv": 0}
VOLTAGES_INV = {2: 0.4, 1: 10, 0: 60}
LAYERS = {
    "CABINET04": 2,
    "STAT1004": 1.5,
    "CONNECTOR10": 1,
    "STAT6010": 0.5,
    "CONNECTOR60": 0,
}
COLUMNS_CABLE = ["from_node", "to_node", "layer"]
COL_TRANS = ["name", "type", "layer"]

_columns_inter_edges = ["upper", "lower", "source", "target"]
_columns_intra_edges = ["source", "target", "layer"]


@pt.fixture(scope="package")
def data_grid() -> Tuple[DataFrame, DataFrame]:
    """Init two dataframes for cables and nodes for a power grid.

    Returns:
        Two dataframes for cables and nodes (intra-nodes and
        transformers).

        .. csv-table::
            :header: name, dtype, definition

            name (index), object, name of inter-node
            from_node, object,
            to_node, object,
            len_km, float64,
            voltage, object,
            r_ohm_per_km, float64,
            c_nf_per_km, float64,
            x_ohm_per_km, float64,
            max_i_ka, float64,
            layer, int

        .. csv-table::
            :header: name, dtype, definition

            name, object, name of inter-node
            type, object,
            layer, float64,

    """
    cables = pd.read_csv("./data/intra-edges.csv", index_col="name")
    cables["layer"] = cables["voltage"].map(VOLTAGES, na_action="ignore")

    nodes = pd.read_csv("./data/nodes.csv")
    nodes["layer"] = nodes["type"].map(LAYERS, na_action="ignore")
    return cables, nodes


@pt.fixture(scope="package")
def grid(data_grid: Tuple[DataFrame, DataFrame]) -> PlanarGrid:
    """Check if a planar grid can be initiated correctly.

    Args:
        data_grid: two dataframes for cables and nodes for a power grid.

    Returns:
        Initiated planar grid.

    """

    def pass_cable_parameters(row):
        return Cable(
            length_km=row["len_km"],
            name=row["name"],
            r_ohm_per_km=row["r_ohm_per_km"],
            x_ohm_per_km=row["x_ohm_per_km"],
            c_nf_per_km=row["c_nf_per_km"],
            max_i_ka=row["max_i_ka"],
            parallel=1,
        )

    cables_raw = data_grid[0].copy(deep=True)
    cables_raw.reset_index(inplace=True)
    cables = cables_raw.loc[:, COLUMNS_CABLE].copy()
    cables["element"] = cables_raw.apply(pass_cable_parameters, axis=1)

    planar = PlanarGrid.from_edgelist(
        cables, "from_node", "to_node", "element"
    )

    assert planar.layers == {1, 2}
    assert list(planar.inter_nodes.columns) == COLUMNS + ["element"]

    # Add transformer types.
    planar.types["STAT6010"] = TransformerType(
        s_mva=8000 / 1e3,
        v_high_kv=60,
        v_low_kv=10,
        vk_percent=10,
        vkr_percent=0.6,
        pfe_kw=12,
        i0_percent=0.15001,
    )
    planar.types["STAT1004"] = TransformerType(
        s_mva=250 / 1e3,
        v_high_kv=10,
        v_low_kv=0.4,
        vk_percent=4,
        vkr_percent=1.2,
        pfe_kw=0.82,
        i0_percent=0.32801,
    )

    # Add the only 60-10 kV transformer.
    planar.add_inter_node(
        "EVO_6777175", TransformerStd("STAT6010", "EVO_6777175", parallel=1)
    )

    # Add all the 10-0.4 kV transformer.
    inter_nodes = data_grid[1].loc[
        data_grid[1]["layer"].isin([0.5, 1.5]), COL_TRANS
    ]
    for _, row in inter_nodes.iterrows():
        if not row["type"] == "STAT6010":
            planar.add_inter_node(
                row["name"],
                TransformerStd("STAT1004", row["name"], parallel=1),
            )

    # Check if inter-nodes are specified correctly.
    assert set(planar.inter_nodes.index) == set(inter_nodes["name"])

    assert planar.intra_nodes.shape == (174, 1)
    assert planar.intra_nodes.index.name == "name"

    # Check dataframe for conversion elements.
    assert list(planar.conversions.columns) == ["node", "element", "layer"]
    assert planar.conversions.index.name == "name"

    return planar


@pt.fixture(scope="package")
def planar_graph(data_grid: DataFrame) -> PlanarGraph:
    """Init a case with 207 edges and **voltage** attributes.

    Note:
        - The dataset used has not been uploaded.
        - "EVO_6777175" is not recognised as inter-node directly,
          because there is no intra-edge in layer 0. Also, layer 0 does
          not exist, because there is no intra-edge there.
        - "EVO_2100520" is not recognised as inter-node directly as
          well, because there is no intra-edge in layer 2 connecting to
          it.

    Args:
        data_grid: two dataframes for cables and nodes for a power grid.

    Returns:
        A case with 208 intra-edges and 34 inter-edges.
    """
    res = PlanarGraph.from_edgelist(data_grid[0], "from_node", "to_node")
    assert res.number_of_edges() == 208

    assert res.layers == {1, 2}
    res.add_inter_node("EVO_6777175")
    res.add_inter_node("EVO_2100520", upper=False)
    assert res.layers == {0, 1, 2}

    inter_nodes = set(
        data_grid[1]
        .loc[data_grid[1]["layer"].isin([0.5, 1.5]), "name"]
        .unique()
    )
    assert set(res.inter_nodes.index) == inter_nodes
    return res


def test_graph(planar_graph: PlanarGraph):
    """Check the case with 208 intra-edges and 34 inter-edges.

    Args:
        planar_graph: the case with 208 intra-edges and 34 inter-edges.
    """
    res = planar2supra(planar_graph)

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


def test_planar_grid(grid: PlanarGrid):
    """Check if ``PlanarGrid`` can be converted correctly.

    Args:
        grid: initiated planar grid.
    """
    res = planar2supra(grid)
    buses = deepcopy(res.nodelist)
    buses["voltage"] = buses["layer"].map(VOLTAGES_INV)

    net = supra2pandapower(res, buses)
    print(net)
