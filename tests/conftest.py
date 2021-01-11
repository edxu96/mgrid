"""Configure tests for ``vsec``."""
import networkx as nx
import pytest as pt


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
def case_readme() -> nx.Graph:
    """Init the test case shown in README file.

    Returns:
        A test case shown in README file.
    """
    res = nx.Graph()
    res.add_edge("a", "g", level="high")
    res.add_edge("c", "g", level="high")
    res.add_edge("d", "g", level="low")
    res.add_edge("f", "g", level="low")
    return res
