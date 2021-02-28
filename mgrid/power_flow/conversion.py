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

import pandapower as pp
from pandapower.auxiliary import pandapowerNet


@dataclass
class Ejection:
    """Essential parameters for load or static generators.

    Note:
        - The power factor of such ejection model is usually
          time-invariant.
    """

    p_mw: float  #: ejected real power in mega-watt
    power_factor: float  #: power factory

    @property
    def q_mvar(self) -> float:
        """Calculate ejected reactive power in mega-watt.

        Returns:
            Ejected reactive power in mega-watt.
        """
        return ((self.p_mw / self.power_factor) ** 2 - self.p_mw ** 2) ** 0.5

    def update_pandapower(
        self,
        net: pandapowerNet,
        name: str,
        bus: str,
    ):
        """Update a pandapower model by adding the ejection itself.

        Note:
            When the value of ``p_mw`` is negative, a generator without
            voltage control ability is added.

        Args:
            net: a pandapower network model.
            name: name of the external grid.
            bus: the bus to which the external grid is attached.
        """
        bus_idx = pp.get_element_index(net, "bus", bus)
        if self.p_mw > 0:
            pp.create_load(
                net,
                name=name,
                bus=bus_idx,
                p_mw=self.p_mw,
                q_mvar=self.q_mvar,
                const_i_percent=0,
                const_z_percent=0,
                in_service=True,
            )
        elif self.p_mw < 0:
            pp.create_sgen(
                net,
                name=name,
                bus=bus_idx,
                p_mw=self.p_mw,
                q_mvar=self.q_mvar,
            )


@dataclass
class Capacitor:
    """Define a shunt element representing a capacitor bank.

    Note:
        Capacitor can be seen as a source of reactive power. The value
        may change with respect to voltage.
    """

    q_mvar: float  #: reactive power of the capacitor bank at nominal voltage
    loss_factor: float  #: loss factor tan(delta) of the capacitor bank

    def update_pandapower(
        self,
        net: pandapowerNet,
        name: str,
        bus: str,
    ):
        """Update a pandapower model by adding the capacitor itself.

        Args:
            net: a pandapower network model.
            name: name of the external grid.
            bus: the bus to which the external grid is attached.
        """
        bus_idx = pp.get_element_index(net, "bus", bus)
        pp.create_shunt_as_capacitor(
            net,
            name=name,
            bus=bus_idx,
            q_mvar=self.q_mvar,
            loss_factor=self.loss_factor,
        )


@dataclass
class Slack:
    """Specify one slack bus and its voltage magnitude.

    Note:
        - The external grid or a voltage-controlled conversion element
          is usually attached to this bus. It is not necessary to model
          it.
        - Distributed slack buses should be specified using
          :class:`SlackMulti`, and is supported by ``PyPSA``.
    """

    vm_pu: float = 1.0  #: voltage magnitude in per unit. Default to be 1.

    def update_pandapower(
        self,
        net: pandapowerNet,
        name: str,
        bus: str,
    ):
        """Update a pandapower model by adding the transformer itself.

        Args:
            net: a pandapower network model.
            name: name of the external grid.
            bus: the bus to which the external grid is attached.
        """
        bus_idx = pp.get_element_index(net, "bus", bus)
        pp.create_ext_grid(net, name=name, bus=bus_idx)


@dataclass
class SlackMulti:
    """Specify some bus(es) and/or voltage-controlled element as slack.

    Note:
        See `Power Flow, PyPSA`_ for details.

    .. _Power Flow, PyPSA:
        https://pypsa.readthedocs.io/en/latest/power_flow.html
    """

    pass
