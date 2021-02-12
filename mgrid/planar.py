"""A class for planar graph corresponding to a multilayer network.

All the nodes and edges in a planar graph can have geographical
attributes.
"""
from itertools import chain
from typing import Optional, Set, Tuple, Union

import networkx as nx
import pandas as pd
from pandas.core.frame import DataFrame

from mgrid.log import LOGGER
from mgrid.power_flow.element import (
    Ejection,
    ExternalGrid,
    Transformer,
    TransformerStd,
)

COLUMNS = ["upper", "lower"]
COLUMNS_DI = ["source", "target"]


class PlanarGraph(nx.DiGraph):
    """Multilayer network in form of planar graph.

    Attributes:
        inter_nodes (DataFrame): information on inter-nodes.

            .. csv-table::
                :header: name, dtype, definition

                name (index), object, name in planar graph
                upper, int64, connected upper layer
                lower, int64, connected lower layer

        layers (Set[int]): integer indices of all the layers.

    """

    def __init__(self, dg: Optional[nx.DiGraph] = None):
        """Init an empty directed graph or from existing directed graph.

        Args:
            dg: an existing directed graph. Default to be None.
        """
        if not dg:
            super().__init__()
        else:
            super().__init__(dg)

        self.inter_nodes = None
        self.inter_nodes = self._find_inter_nodes()

        # Find integer indices of all the layers.
        edgelist = nx.to_pandas_edgelist(self)
        if "layer" in edgelist:
            max_layer = edgelist["layer"].max()
            min_layer = edgelist["layer"].min()
            self.layers = set(range(min_layer, max_layer + 1))
        else:
            self.layers = set()

    @classmethod
    def from_edgelist(
        cls,
        df: DataFrame,
        source: str,
        target: str,
        element: Optional[str] = None,
    ):
        """Init a planar graph from an edgelist dataframe.

        Args:
            df: an edgelist with at least three columns.

                .. csv-table::
                    :header: name, dtype, definition

                    layer, int, to which layer an intra-edge belongs
                    element (optional), object, model for intra-edge

            source: column name indicating sources of edges.
            target: column name indicating targets of edges.
            element: column name indicating models for delivery element.

        # noqa: DAR101

        Returns:
            A ``PlanarGraph`` when the dataframe have essential columns.
        """
        if (source not in df) or (target not in df):
            LOGGER.critical(
                f"Column {source} or {target} not found in dataframe."
            )
            res = None
        else:
            if element:
                edge_attr = ["layer", "element"]
            else:
                edge_attr = "layer"
            res = nx.from_pandas_edgelist(
                df,
                source=source,
                target=target,
                edge_attr=edge_attr,
                create_using=nx.DiGraph(),
            )
            res = cls(res)
        return res

    def _find_inter_nodes(self) -> DataFrame:
        """Find as many inter-nodes as possible.

        Returns:
            Dataframe for detected inter-nodes.

            .. csv-table::
                :header: name, dtype, definition

                name (index), name of the node
                upper, int64, upper layer of the inter-edge
                lower, int64, lower layer of the inter-edge

        """
        res_dict = {}
        for node in self.nodes:
            upper, lower = self.find_layer(node)

            if upper == lower - 1:
                res_dict[node] = [upper, lower]
            elif upper == lower:
                pass
            else:
                LOGGER.warning(
                    f"Incorrect specification for node {node} corresponding "
                    f"to an inter-edge with max layer {upper} and min layer "
                    f" {lower}."
                )

        res = pd.DataFrame.from_dict(res_dict, orient="index", columns=COLUMNS)
        res.index.name = "name"
        return res

    @property
    def intra_nodes(self) -> DataFrame:
        """Gather all the intra-nodes in a dataframe.

        Returns:
            A dataframe for intra-nodes.

            .. csv-table::
                :header: name, dtype, definition

                name (index), object, node name
                layer, int64, to which layer the node belongs

        """
        inter_nodes = set(self.inter_nodes.index)
        intra_nodes = [node for node in self.nodes if node not in inter_nodes]
        res = pd.DataFrame(
            [self.find_layer(node)[0] for node in intra_nodes],
            columns=["layer"],
            index=intra_nodes,
        )
        res.index.name = "name"
        return res

    def layer_edges(self, layer: int) -> Set[tuple]:
        """Gather all the edges and edge attributes in one layer.

        Args:
            layer: integer index of a layer.

        Returns:
            An edgelist for those in one layer.
        """
        if layer in self.layers:
            edge_list = nx.to_pandas_edgelist(self)
            res = edge_list[edge_list["layer"] == layer]
        else:
            res = None
        return res

    def layer_graph(self, layer: int) -> nx.DiGraph:
        """Build a directed graph for one layer.

        Note:
            Inter-nodes are not distinguished in different layers.

        Args:
            layer: integer index of a layer.

        Returns:
            A directed graph representing a given layer.
        """
        if layer in self.layers:
            edges = self.layer_edges(layer)
            ite_edges = edges[COLUMNS_DI].itertuples(index=False, name=None)
            res = self.edge_subgraph(ite_edges).copy()
        else:
            res = None
        return res

    def find_layer(self, node: str) -> Tuple[int, int]:
        """Find layer(s) of a given node.

        Note:
            - It is assumed that there is no isolated planar node, or
              its layer must be specified by node attribute.
            - If an inter-node is isolated in some layer, only the other
              layer will be returned.

        Args:
            node: name of a planar node or an inter-node.

        Returns:
            Integer indices of upper and lower layers.
        """
        if (self.inter_nodes is not None) and (node in self.inter_nodes.index):
            upper = self.inter_nodes.loc[node, "upper"]
            lower = self.inter_nodes.loc[node, "lower"]
        else:
            layers = [
                layer
                for _, _, layer in chain(
                    self.in_edges(node, data="layer"),
                    self.out_edges(node, data="layer"),
                )
            ]

            upper = min(layers)
            lower = max(layers)

        return (upper, lower)

    def add_inter_node(self, name: str, upper: Optional[bool] = True):
        """Specify a planar node as an inter-node with an adjacent layer.

        Sometimes, one terminal of an inter-edge is an isolated node in some
        layer, then it will not be recognised as an inter-node. It must be
        specified manually.

        Warning:
            Upper layer has a smaller integer index.

        Args:
            name: name of the inter-node.
            upper: whether the other terminal of the corresponding
                inter-edge is on upper layer.
        """
        if name not in self.nodes:
            LOGGER.error(f"Node {name} does not exist.")
        elif name in self.inter_nodes.index:
            LOGGER.error(f"Inter-node {name} already exist.")
        else:
            layer = self.find_layer(name)[0]
            if upper:
                upper = layer - 1
                lower = layer

                if upper not in self.layers:
                    self.layers.add(upper)
                    LOGGER.info(
                        f"New top layer {upper} resulted from node {name}."
                    )
            else:
                upper = layer
                lower = layer + 1

                if lower not in self.layers:
                    self.layers.add(lower)
                    LOGGER.info(
                        f"New bottom layer {lower} resulted from {name}."
                    )

            df_new = pd.DataFrame(
                {"upper": upper, "lower": lower}, index=[name]
            )
            self.inter_nodes = self.inter_nodes.append(df_new)
            LOGGER.debug(
                f"New inter-node {name} for layer {upper} and {lower}."
            )


class PlanarGrid(PlanarGraph):
    """Model multilayer graph in plane by contracting inter-edges.

    Note:
        There are two kinds of nodes, inter-nodes and planar nodes. If
        an inter-node is isolated in some layer, it cannot be recognised
        directly.

    Attributes:
        inter_nodes (DataFrame): information on inter-nodes.

            .. csv-table::
                :header: name, dtype, definition

                name (index), object, name in planar graph
                upper, int64, connected upper layer
                lower, int64, connected lower layer
                element, object, transformer model

        layers (Set[int]): integer indices of all the layers.
        conversion (DataFrame): information on conversion elements.

            .. csv-table::
                :header: name, dtype, definition

                name (index), object, name of conversion elements.
                node, object, nodes to which elements are attached.
                element, object, element models.
                layer, int64, layers to which elements belong.

    """

    def __init__(self, dg: Optional[nx.DiGraph] = None):
        """Init an empty directed graph or from existing directed graph.

        Note:
            - All the edges are intra-edges, so they must be associated
              with some layer.
            - It is essential to have the option for empty graph, or
              some built-in ``networkx`` function will not work. Don't
              know why.
            - Most inter-nodes can be detected. However, when one
              terminal of some inter-edge is isolated in that layer, the
              corresponding inter-node cannot be detected.

        Args:
            dg: an existing directed graph. Default to be None.
        """
        if not dg:
            super().__init__()
        else:
            super().__init__(dg)

        self.inter_nodes["element"] = None

        # Init the dataframe for conversion elements.
        self.conversions = pd.DataFrame(
            {"name": [], "node": [], "element": [], "layer": []}
        )
        self.conversions.set_index("name", inplace=True)

        # Init the dictionary for element types.
        self.types = {}

    def add_inter_node(
        self,
        name: str,
        element: Union[Transformer, TransformerStd],
        upper: Optional[bool] = True,
    ):
        """Specify a planar node as an inter-node with an adjacent layer.

        Sometimes, one terminal of an inter-edge is an isolated node in some
        layer, then it will not be recognised as an inter-node. It must be
        specified manually.

        Warning:
            Upper layer has a smaller integer index.

        Args:
            name: name of the inter-node.
            element: the transformer model.
            upper: whether the other terminal of the corresponding
                inter-edge is on upper layer.
        """
        super().add_inter_node(name, upper)
        self.inter_nodes.loc[name, "element"] = element

    def add_conversion(
        self,
        name: str,
        node: str,
        element: Union[Ejection, ExternalGrid],
        layer: Optional[str] = None,
    ):
        """Add a conversion element to the grid.

        Note:
            Any conversion element is associated with a layer. If it is
            attached to a intra-node, then it inherent the node's layer.
            If to a inter-node, ``layer`` should be specified.

        Args:
            name: name of the conversion element.
            node: name of the node to which the element is attached.
            element: model for the element.
            layer: layer to which the element belongs. If ``node`` is an
                intra-node, it is not necessary to specify it. When
                ``node`` is an inter-node and it is not specified, a
                warning will be echoed.
        """
        if node in self.nodes:
            upper, lower = self.find_layer(node)

            if not layer and upper == lower:
                layer = upper
            elif not layer and upper < lower:
                LOGGER.warning(
                    f'Layer of conversion element "{name}" is not specified.'
                )

            _new = pd.DataFrame(
                {"node": node, "element": element, "layer": layer},
                index=[name],
            )
            self.conversions = self.conversions.append(_new)
            LOGGER.debug(
                f'New conversion element "{element}" called "{name}" is '
                f'attached to node "{node}."'
            )
        else:
            LOGGER.error(f'There is no node called "{node}".')
