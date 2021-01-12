"""Configure unit tests in ``vsec``."""
import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame
import pytest as pt

# Dictionary to map entries in a column.
VOLTAGES = {
    "04kv": 0.4,
    "10kv": 10,
    "60kv": 60,
}


@pt.fixture(scope="package")
def case_simple() -> nx.Graph:
    """Init a simple test case with three edges.

    Returns:
        A simple test case with three edges.
    """
    res = nx.Graph()
    res.add_edge("n1", "n2", contraction=False)
    res.add_edge("n2", "n3", contraction=True)
    res.add_edge("n3", "n4", contraction=False)
    return res


@pt.fixture(scope="package")
def case_readme() -> nx.DiGraph:
    """Init the test case shown in README file.

    Returns:
        A test case shown in README file.
    """
    res = nx.DiGraph()
    res.add_edge("a", "g", level="high")
    res.add_edge("c", "g", level="high")
    res.add_edge("d", "g", level="low")
    res.add_edge("f", "g", level="low")
    return res


@pt.fixture(scope="package")
def case_grid() -> nx.Graph:
    """Init a case with 207 edges and **voltage** attributes.

    Note:
        The dataset used has not been uploaded.

    Returns:
        A case with 207 edges.
    """
    df = pd.read_csv("./data/curves.csv", index_col="name")
    df["voltage"] = df["voltage"].map(VOLTAGES, na_action="ignore")

    res = nx.from_pandas_edgelist(
        df, source="from_node", target="to_node", edge_attr=["voltage"]
    )
    assert nx.is_connected(res)
    return res


@pt.fixture(scope="package")
def vertices_grid() -> DataFrame:
    """Gather vertices in ``case_grid`` and their **type** attributes.

    Note:
        The dataset used has not been uploaded.

    Returns:
        Vertices in ``case_grid`` and their **type** attributes.
    """
    df = pd.read_csv("./data/vertices.csv", index_col="name")
    return df
