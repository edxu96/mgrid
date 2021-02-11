"""Configure unit tests in ``vsec``."""
from typing import Tuple

import pandas as pd
from pandas.core.frame import DataFrame
import pytest as pt

from mgrid.planar import PlanarGraph
from .test_planar import simple  # noqa: F401

# Dictionary to map entries in column "voltage" to layers.
VOLTAGES = {"04kv": 2, "10kv": 1, "60kv": 0}
LAYERS = {
    "CABINET04": 2,
    "STAT1004": 1.5,
    "CONNECTOR10": 1,
    "STAT6010": 0.5,
    "CONNECTOR60": 0,
}


@pt.fixture(scope="package")
def case_large() -> PlanarGraph:
    """Init a case with 8 planar edges and 2 inter-edges.

    Returns:
        A test case with 8 planar edges and 2 inter-edges.
    """
    df = pd.read_csv("./tests/planar_large.csv")
    res = PlanarGraph.from_edgelist(df, "source", "target")
    res.add_inter_node("n3", upper=False)

    assert res.number_of_edges() == 8
    assert res.number_of_nodes() == 7
    return res


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
def case_grid(data_grid: DataFrame) -> PlanarGraph:
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
