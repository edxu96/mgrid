"""Configure unit tests in ``vsec``."""
import pandas as pd
import pytest as pt

from mgrid.planar import PlanarGrid
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
def case_grid() -> PlanarGrid:
    """Init a case with 207 edges and **voltage** attributes.

    Note:
        - The dataset used has not been uploaded.
        - "EVO_6777175" is not recognised as inter-node directly,
          because there is no intra-edge in layer 0. Also, layer 0 does
          not exist, because there is no intra-edge there.
        - "EVO_2100520" is not recognised as inter-node directly as
          well, because there is no intra-edge in layer 2 connecting to
          it.

    Returns:
        A case with 208 intra-edges and 34 inter-edges.
    """
    df = pd.read_csv("./data/intra-edges.csv", index_col="name")
    df["layer"] = df["voltage"].map(VOLTAGES, na_action="ignore")

    res = PlanarGrid.from_edgelist(df, "from_node", "to_node")
    assert res.number_of_edges() == 208

    assert res.layers == {1, 2}
    res.add_inter_node("EVO_6777175")
    res.add_inter_node("EVO_2100520", upper=False)
    assert res.layers == {0, 1, 2}

    nodes = pd.read_csv("./data/nodes.csv")
    nodes["layer"] = nodes["type"].map(LAYERS, na_action="ignore")
    inter_nodes = set(
        nodes.loc[nodes["layer"].isin([0.5, 1.5]), "name"].unique()
    )
    assert set(res.inter_nodes.index) == inter_nodes
    return res
