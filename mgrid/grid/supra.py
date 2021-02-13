"""Class for grid in supra-graph format."""
from typing import Optional

import networkx as nx

from mgrid.graph.supra import SupraGraph


class SupraGrid(SupraGraph):
    """Power grid modelled as supra-graph.

    Warning:
        Modification is impossible for now.

    Attributes:
        conversions (DataFrame):

            .. csv-table::
                :header: name, dtype, definition

                name (index), object, name of conversion elements.
                bus, object, buses to which elements are attached.
                element, object, element models.

        types (dict): standard element types, keyed by type names.

    """

    def __init__(self, dg: Optional[nx.DiGraph] = None):
        """Init an empty directed graph or existing directed graph.

        Note:
            It is essential to have the option for empty graph, or some
            built-in ``networkx`` function will not work. Don't know
            why.

        Args:
            dg: an existing directed graph. Default to be None.
        """
        if not dg:
            super().__init__()
        else:
            super().__init__(dg)

        self.conversions = None
        self.types = None
