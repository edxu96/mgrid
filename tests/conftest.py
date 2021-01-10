"""Configure tests for ``vsec``."""
import networkx as nx
import pytest as pt


@pt.fixture(scope='package')
def case_simple() -> nx.Graph:
    res = nx.Graph()
    res.add_edge('n1', 'n2', contraction=False)
    res.add_edge('n2', 'n3', contraction=True)
    res.add_edge('n3', 'n4', contraction=False)
    return res
