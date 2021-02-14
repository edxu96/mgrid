"""Prototypical classes for conversion elements in power flow analysis.

A **conversion element** is an electrical device converting electricity
to or from other form. For example, a microware oven relies on
electricity to emit wave. Such devices have only one terminal and must
be attached to a bus. Generally, based on if the neutral wire is
involved, there are two kinds of connection: wye or delta. Wye
connection is the focus for now. A bus can have multiple or zero
conversion element attached.

For any conversion element, a unique name and a node to which it
attaches must be specified in supra graph. Furthermore, in planar graph,
the layer of the element must be specified, because it might be attached
to an inter-node, which spans two layers. See
:mod:`mgrid.grid.planar` for more details.
"""
from dataclasses import dataclass

from pandapower.auxiliary import pandapowerNet


@dataclass
class Ejection:
    """Essential parameters for load or static generators."""

    p_mw: float  #: ejected real power in mega-watt
    power_factor: float  #: power factory

    @property
    def q_mw(self) -> float:
        """Calculate ejected reactive power in mega-watt.

        Returns:
            Ejected reactive power in mega-watt.
        """
        return ((self.p_mw / self.power_factor) ** 2 - self.p_mw ** 2) ** 0.5


@dataclass
class ExternalGrid:
    """Define a slack bus and a corresponding external grid.

    Note:
        It's assumed that there is only one slack bus and one external
        grid.
    """

    vm_pu: float = 1.0  #: voltage magnitude in per unit. Default to be 1.

    def update_pandapower(
        self, net: pandapowerNet, name: str, bus: str,
    ):
        """Update a pandapower model by adding the transformer itself.

        Args:
            net: a pandapower network model.
            name: name of the external grid.
            bus: the bus to which the external grid is attached.
        """
        net.add("Generator", name=name, bus=bus, control="Slack")
