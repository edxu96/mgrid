"""Configure unit tests in ``vsec``."""
import pandas as pd
import pytest as pt

from mgrid.planar import PlanarGraph
from .test_planar import simple  # noqa: F401

# Dictionary to map entries in column "voltage" to layers.
VOLTAGES = {
    "04kv": 2,
    "10kv": 1,
    "60kv": 0,
}


@pt.fixture(scope="package")
def case_grid() -> PlanarGraph:
    """Init a case with 207 edges and **voltage** attributes.

    Note:
        - The dataset used has not been uploaded.
        - "EVO_6777175" is not recognised as inter-node directly,
          because there is no intra-edge in layer 0. Also, layer 0 does
          not exist, because there is no intra-edge there.

    Returns:
        A case with 208 intra-edges and 34 inter-edges.
    """
    df = pd.read_csv("./data/intra-edges.csv", index_col="name")
    df["layer"] = df["voltage"].map(VOLTAGES, na_action="ignore")

    res = PlanarGraph.from_edgelist(df, "from_node", "to_node")
    assert res.number_of_edges() == 208

    assert res.layers == {1, 2}
    res.add_inter_node("EVO_6777175")
    assert res.layers == {0, 1, 2}
    return res
