"""Define data-classes for elements.

.. note::
    Whether the element is paralleled should be specified as an edge
    attribute.

.. warning::
    Inherited attributes are not shown again.

"""
from dataclasses import dataclass

import pandapower as pp
from pandapower.auxiliary import pandapowerNet


@dataclass
class CableEssential:
    """Essential cable parameters."""

    length_km: float  #: cable length in kilometer
    name: str  #: name


@dataclass
class Cable(CableEssential):
    """Define cable from parameters."""

    r_ohm_per_km: float  #: resistance in ohm per kilo-meter
    x_ohm_per_km: float  #: reactance in ohm per kilo-meter
    c_nf_per_km: float  #: capacitance in nano Farad per kilo-meter
    max_i_ka: float  #: maximum thermal current in kilo-ampere

    def update_pandapower(
        self, net: pandapowerNet, source: str, target: str, parallel: int,
    ):
        """Update a pandapower model by adding the cable itself.

        Args:
            net: a pandapower network model.
            source: a bus of the cable, corresponding to ``source`` in
                ``networkx`` edge.
            target: another bus of the cable, corresponding to ``source`` in
                ``networkx`` edge.
            parallel: number of same cables in parallel.
        """
        from_bus = pp.get_element_index(net, "bus", source)
        to_bus = pp.get_element_index(net, "bus", target)
        pp.create_line_from_parameters(
            net,
            name=self.name,
            from_bus=from_bus,
            to_bus=to_bus,
            length_km=self.length_km,
            r_ohm_per_km=self.r_ohm_per_km,
            x_ohm_per_km=self.x_ohm_per_km,
            c_nf_per_km=self.c_nf_per_km,
            max_i_ka=self.max_i_ka,
            parallel=parallel,
        )


@dataclass
class CableStd(CableEssential):
    """Define cable from standard type."""

    std_type: str  #: a standard cable type


@dataclass
class TransformerStd:
    """Essential transformer parameters."""

    std_type: str  #: a standard transformer type
    name: str  #: name of the inter-node

    def update_pandapower(
        self, net: pandapowerNet, source: str, target: str, parallel: int,
    ):
        """Update a pandapower model by adding the transformer itself.

        Args:
            net: a pandapower network model.
            source: a bus of the transformer, corresponding to ``source`` in
                ``networkx`` edge.
            target: another bus of the transformer, corresponding to
                ``source`` in ``networkx`` edge.
            parallel: number of same cables in parallel.
        """
        hv_bus = pp.get_element_index(net, "bus", source)
        lv_bus = pp.get_element_index(net, "bus", target)
        pp.create_transformer(
            net,
            name=self.name,
            hv_bus=hv_bus,
            lv_bus=lv_bus,
            std_type=self.std_type,
            parallel=parallel,
        )


@dataclass
class Transformer:
    """Define transformer from parameters."""

    pass


@dataclass
class Ejection:
    """Essential parameters for load or static generators."""

    p_mw: float  #: ejected real power in mega-watt
    q_mvar: float  #: ejected reactive power in mega-watt


@dataclass
class ExternalGrid:
    """Define a slack bus and a corresponding external grid.

    Note:
        It's assumed that there is only one slack bus and one external
        grid.
    """

    vm_pu: float  #: voltage magnitude in per unit

    def update_pandapower(
        self, net: pandapowerNet, bus: str,
    ):
        """Update a pandapower model by adding the transformer itself.

        Args:
            net: a pandapower network model.
            bus: the bus to which the external grid is attached.
        """
        net.add(
            "Generator", name="ExternalGrid_60kV", bus=bus, control="Slack"
        )
