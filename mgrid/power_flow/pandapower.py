"""Build pandapower model.

Three functions to add buses, delivery elements, and conversion elements.
"""
import networkx as nx
import pandapower as pp
from pandapower.auxiliary import pandapowerNet

from mgrid.grid import SupraGrid
from mgrid.log import LOGGER


def _complete_edge_attr(g, attr: str) -> bool:
    """Check if all edges in the graph have the given attribute.

    Args:
        g: a networkx graph
        attr: name of an edge attribute.

    Returns:
        bool: true if all nodes in the graph have the given attribute.
    """
    res = True
    num_edges = len(g.edges)
    dict_edge_attr = nx.get_edge_attributes(g, attr)
    if len(dict_edge_attr) < num_edges:
        LOGGER.critical(
            f"There are {num_edges - len(dict_edge_attr)} edges "
            f'without the attribute "{attr}".'
        )
        res = False
    return res


def supra2pandapower(supra: SupraGrid) -> pandapowerNet:
    """Build ``pandapower`` model based on supra format.

    Args:
        supra: a supra-grid.

    Returns:
        A ``pandapower`` model.
    """
    # Check if all the edges have the "element" attribute.
    _complete_edge_attr(supra, "element")

    # Init an empty pandapower model.
    net = pp.create_empty_network()

    # Add all the element types.
    for key, std_type in supra.types.items():
        std_type.update_pandapower(net, key)

    # Add all the buses.
    for node, row in supra.nodelist.iterrows():
        pp.create_bus(net, name=node, vn_kv=row["voltage"])

    # Add all the delivery elements.
    for source, target, data in supra.edges.data():
        data["element"].update_pandapower(net, source, target)

    # Add all the conversion elements (if any).
    for name, row in supra.conversions.iterrows():
        row["element"].update_pandapower(net, name, row["bus"])

    return net
