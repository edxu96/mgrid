"""Function to convert planar graph to supra-graph."""
from copy import deepcopy
from itertools import chain
from typing import Tuple

import networkx as nx
import pandas as pd

from mgrid.log import LOGGER
from mgrid.multilayer import SupraGrid
from mgrid.planar import COLUMNS, COLUMNS_DI, PlanarGrid

COLUMNS_DI_ORIGINAL = ["source_original", "target_original"]


def planar2supra(g: PlanarGrid) -> SupraGrid:
    """Convert a planar graph to corresponding supra-graph.

    Args:
        g: a planar graph to be converted.

    Returns:
        Resulted supra-graph.
    """
    dg = nx.DiGraph(g)

    # Initiate dictionary for nodes in different layers.
    node_dict = {}
    inter_nodes = set(g.inter_nodes.index)
    for layer in g.layers:
        node_dict[layer] = set(g.layer_graph(layer).nodes) - inter_nodes

    # Initiate dataframe for inter-edges.
    inter_edges = deepcopy(g.inter_nodes)
    inter_edges["source"] = "default_"
    inter_edges["target"] = "default_"

    # Initiate dataframe for intra-edges.
    intra_edges = nx.to_pandas_edgelist(g)
    intra_edges[COLUMNS_DI_ORIGINAL[0]] = intra_edges[COLUMNS_DI[0]]
    intra_edges[COLUMNS_DI_ORIGINAL[1]] = intra_edges[COLUMNS_DI[1]]
    intra_edges.set_index(COLUMNS_DI_ORIGINAL, inplace=True)

    def update_intra_edges(edge: Tuple[str, str], edge_new: Tuple[str, str]):
        """Update intra-edges' relationship after splitting inter-nodes.

        Args:
            edge: intra-edges in planar graph.
            edge_new: corresponding edge in supra-graph.
        """
        edges_original = intra_edges.index[
            (intra_edges[COLUMNS_DI[0]] == edge[0])
            & (intra_edges[COLUMNS_DI[1]] == edge[1])
        ].tolist()
        if len(edges_original) != 1:
            LOGGER.error(f"The origin of edge {edge} is incorrect.")
        intra_edges.loc[edges_original[0], COLUMNS_DI] = edge_new

    # Split all the inter-nodes to inter-edges.
    for node, row in g.inter_nodes.iterrows():
        in_edges = list(dg.in_edges(nbunch=node, data=True))
        for u, _, data in in_edges:
            edge_new = (u, str(node) + f'_layer{data["layer"]}')
            dg.add_edge(*edge_new, **data)
            update_intra_edges((u, node), edge_new)
        out_edges = list(dg.out_edges(nbunch=node, data=True))
        for _, v, data in out_edges:
            edge_new = (str(node) + f'_layer{data["layer"]}', v)
            dg.add_edge(*edge_new, **data)
            update_intra_edges((node, v), edge_new)

        def init_node4inter(binary: int) -> str:
            """Init source or target for the inter-edge.

            Args:
                binary: 0 or 1, representing "source" and "target".

            Returns:
                Node name of source or target.
            """
            layer = row[COLUMNS[binary]]
            node_new = str(node) + f"_layer{layer}"
            inter_edges.loc[node, COLUMNS_DI[binary]] = node_new
            node_dict[layer].add(node_new)
            return node_new

        source = init_node4inter(0)
        target = init_node4inter(1)
        dg.add_edge(source, target)

        dg.remove_node(node)

    # Build nodelist using dictionary for nodes in different layers.
    keys_sorted = sorted(node_dict)
    nodelist = pd.DataFrame(
        {
            "layer": chain(
                *[[key] * len(node_dict[key]) for key in keys_sorted]
            )
        },
        index=chain(*[node_dict[key] for key in keys_sorted]),
    )

    # Build supra-grid.
    res = SupraGrid(dg)
    res.intra_edges = intra_edges
    res.inter_edges = inter_edges
    res.inter_edges.index.name = "node"
    res.nodelist = nodelist
    return res
