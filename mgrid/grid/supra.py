"""Class for power grid as multilayer network in supra-graph format.

Any node in a supra graph is a **bus**, which is an imaginary concept to
enforce Kirchhoff's law. It can a conjunction of two cables or an entire
nation. There is no power loss within any bus. When aggregating some
area (like an entire country) as a bus, the loss within that area can be
represented by a conversion element. However, it is impossible to derive
the loss correctly.

Usually, in the literature, three types of buses, PQ, PV, and slack, are
considered, but it is not necessary. Those features are resulted from
attached conversion elements. There is only one type of node here.
"""
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
