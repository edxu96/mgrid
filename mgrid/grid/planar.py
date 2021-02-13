"""Class for grid in planar graph format."""
from typing import Optional, Union

import networkx as nx
import pandas as pd

from mgrid.graph.planar import PlanarGraph
from mgrid.log import LOGGER
from mgrid.power_flow.conversion import Ejection, ExternalGrid
from mgrid.power_flow.delivery import Transformer, TransformerStd


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
        if name not in self.inter_nodes.index:
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
